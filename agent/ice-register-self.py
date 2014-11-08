#!/usr/bin/env python
##########################################################################
# Name:
#   ice-register-self.py
#
# Description:
#   Registers virtual instance that calls this script to iCE.
#
# Usage:
#   ice-register-self.py -a|--api <API endpoint URL> -e|--exp <Experiment key>
#       [-v|--verbose]
#   -a|--api <API endpoint URL> The iCE RESTful API endpoint. Can be omitted if
#       ICE_API_ENDPOINT environment variable is set.
#   -e|--exp <Experiment key> The experiment key. Can be omitted if ICE_EXP_KEY
#       environment variable is set.
#   -v|--verbose Verbose option.
##########################################################################
import re
import subprocess
import os
import sys
import getpass
import base64
import hashlib
import getopt
import urllib2
import json


#
# Globals
#

___version__ = '0.0.1'
IS_ROOT = False  # is the user root?


#
# Helpers: run commands
#

def _run_sudo(cmd):
    global IS_ROOT
    if IS_ROOT:
        return _run(cmd)
    return _run('sudo -n %s' % cmd)


def _run(cmd):
    args = cmd.split()
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    proc.wait()
    stdout = proc.stdout.read()
    proc.stdout.close()
    stderr = proc.stderr.read()
    proc.stderr.close()
    return (stdout, stderr)


#
# Helpers: SSH
#

def key_to_fingerprint(key):
    key = base64.b64decode(key.strip().encode('ascii'))
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))


def _extract_first_fingerprint(file_path):
    # Open file
    if not os.path.isfile(file_path):
        return None
    auth_keys = open(file_path)
    if auth_keys is None:
        return None

    # Find first SSH key in file
    reg_ex = re.compile(r'^ssh-rsa\s*([^\s]*).*$')
    for ssh_line in auth_keys:
        match = re.match(reg_ex, ssh_line)
        if match is None:  # unknown format
            continue
        fingerprint = key_to_fingerprint(match.group(1))
        if fingerprint is not None:
            # fingerprint build!
            auth_keys.close()
            return fingerprint

    # Failed
    auth_keys.close()
    return None


#
# Helpers: steps
#

def _is_root():
    """
    Detects if the user is or can be (password-less) a root (through sudo).

    :rtype: bool
    :return: True if user is or can be root, False otherwise.
    """
    global IS_ROOT
    if getpass.getuser() != 'root':
        IS_ROOT = False
        (out, err) = _run('sudo -n whoami')
        if out.strip() != 'root':
            return False
    else:
        IS_ROOT = True
    return True


def _parse_cmd(args):
    """
    Parses the command line arguments.

    :param list args: The `sys.argv` contents.
    :rtype: dict|None
    :return: A dictionary with parsed options or `None` in case of error.
    """
    # Set defaults
    ret_val = {
        'verbose': False,
        'apiEndpoint': os.environ.get('ICE_API_ENDPOINT', None),
        'experimentKey': os.environ.get('ICE_EXP_KEY', None),
    }

    # Parse
    try:
        optlist, args = getopt.getopt(
            args, 'a:e:v', ['api=', 'exp=', 'verbose']
        )
    except getopt.GetoptError as err:
        print '[ERROR] %s' % str(err)
        return None
    for o, a in optlist:
        if o in ('--verbose', '-v'):
            ret_val['verbose'] = True
        elif o in ('--exp', '-e'):
            ret_val['experimentKey'] = a
        elif o in ('--api', '-a'):
            ret_val['apiEndpoint'] = a
        else:
            print '[ERROR] Option `%s` is unknown!' % o
            return None

    # Validate
    if ret_val['apiEndpoint'] is None:
        print '[ERROR] Please specify the API endpoint URL using the -a or' \
            + ' --api argument!'
        return None
    if ret_val['experimentKey'] is None:
        print '[ERROR] Please specify the experiment key using -e or --exp' \
            + ' argument!'
        return None

    return ret_val


def _extract_networks():
    """
    Extracts list of IPv4 networks.

    :rtype: list
    :return: list of tuples `(<Interface>, <Network>, <Broadcast address>)`.
    """
    ret_val = []
    reg_ex = re.compile(
        r'^[0-9]*\:\s*([a-z0-9]*)\s*inet\s*([0-9\.\/]*)\s*brd\s*([0-9\.]*).*$'
    )
    (out, err) = _run_sudo('ip -o -f inet addr show')
    for line in out.split('\n'):
        match = reg_ex.match(line)
        if match is None:
            continue
        ret_val.append((match.group(1), match.group(2), match.group(3)))
    return ret_val


def _extract_ssh_info():
    """
    Extracts the user name of the user that has an SSH public key installed,
    and the fingerprint of than key.

    :rtype: tuples
    :return: An (<SSH user name>, <SSH authorized key fingerprint>) tuple.
    """
    # Open users file
    passwd = open('/etc/passwd')
    if passwd is None:
        return None

    # Iterate through all users
    for line in passwd:
        # Get username and directory
        parts = line.split(':')
        user_name = parts[0]
        home_dir_path = parts[5]
        if home_dir_path == '' or home_dir_path == '/':
            continue

        # Look for first SSH key
        fingerprint = _extract_first_fingerprint(
            '%s/.ssh/authorized_keys' % home_dir_path
        )
        if fingerprint is not None:
            passwd.close()
            return (user_name, fingerprint)

    # Failed
    passwd.close()
    return None


def _get_cloud_info():
    """
    Gets cloud information.

    :rtype: tuple
    :return: A tuple with (<Cloud id>, <VPC id>)
    """
    # Check environment variables
    cloud_id = os.environ.get('ICE_CLOUD_ID', None)
    vpc_id = os.environ.get('ICE_VPC_ID', None)

    return cloud_id, vpc_id


def _make_request():
    ret_val = {}

    #  Network information
    networks = _extract_networks()
    if networks is None:
        print '[ERROR] Failed to extract networking info...'
        return None
    ret_val['networks'] = []
    for n in networks:
        iface, addr, bcast = n
        ret_val['networks'].append(
            {
                'interface': iface,
                'address': addr,
                'broadcast': bcast
            }
        )

    # SSH information
    r = _extract_ssh_info()
    if r is None:
        print '[ERROR] Failed to extract SSH info...'
        return None
    ssh_username, ssh_authorized_fingerprint = r
    if ssh_username is not None:
        ret_val['ssh_username'] = ssh_username
    ret_val['ssh_authorized_fingerprint'] = ssh_authorized_fingerprint

    # Cloud information
    info = _get_cloud_info()
    if info is None:
        print '[ERROR] Failed to get cloud info...'
        return None
    cloud_id, vpc_id = info
    if cloud_id is not None:
        ret_val['cloud_id'] = cloud_id
    if vpc_id is not None:
        ret_val['vpc_id'] = vpc_id

    return ret_val


#
# Main
#

if __name__ == '__main__':
    # Check if the user is or can be root
    if not _is_root():
        print '[ERROR] This script must run as root or as a non-password' \
            + ' sudoer!'
        sys.exit(1)

    # Parse the command line
    cmd = _parse_cmd(sys.argv[1:])
    if cmd is None:
        print '[ERROR] Failed to parse command line arguments!'
        sys.exit(1)

    # Get the request
    ice_req = _make_request()
    if len(ice_req) == 0:
        print '[ERROR] Failed to build the request!'
        sys.exit(1)

    # Make the request
    try:
        req = urllib2.Request(
            cmd['apiEndpoint'],
            json.dumps(ice_req),
            {
                'Content-Type': 'application/json',
                'User-Agent': 'iCE Agent/%s' % ___version__,
                'Experiment-Key': hashlib.sha1(cmd['experimentKey'])
            }
        )
        http_req = urllib2.urlopen(req)
    except ValueError as err:
        print '[ERROR] Nasty error: %s' % str(err)
        sys.exit(1)
    except urllib2.HTTPError as err:
        print '[ERROR] HTTP error: %s' % str(err)
        sys.exit(1)

    import pprint
    pprint.pprint(cmd)
    pprint.pprint(ice_req)
    pprint.pprint(http_req)

    sys.exit(0)
