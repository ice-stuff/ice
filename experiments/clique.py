"""A test experiment"""
import os
import re
import json

import matplotlib.pyplot as plt
from fabric import api as fab

import ice


#
# Configuration
#

DEF_SENT_BYTES_AMT = 536870912


#
# Runners
#

@ice.Runner
def re_plot(hosts, results_dir_path=None):
    """Re-plots the graphs."""
    if results_dir_path is None:
        results_dir_path = os.path.abspath(os.path.dirname(__file__))

    data_file_path = os.path.join(results_dir_path, 'data.json')
    if not os.path.isfile(data_file_path):
        print 'ERROR: File `%s` not found!' % data_file_path
        return

    # Read file
    f = open(data_file_path)
    d = json.loads(f.read())
    f.close()

    # Re-plot
    out_file_path, in_file_path = _plot(results_dir_path, d['out'], d['in'])

    # Print
    print 'Look for %s and %s.' % (out_file_path, in_file_path)


@ice.Runner
def run(hosts, results_dir_path=None, sent_bytes_amt=DEF_SENT_BYTES_AMT):
    """Runs the tutorial."""
    if results_dir_path is None:
        results_dir_path = os.path.abspath(os.path.dirname(__file__))

    # Copy keys
    fab.execute(copy_key, hosts)

    # Experimentation
    in_timings = []
    out_timings = []
    res = fab.execute(ping, hosts, sent_bytes_amt)
    for key, ret_val in res.items():
        ot, it = ret_val
        out_timings += ot
        in_timings += it

    # Write data
    f = open(os.path.join(results_dir_path, 'data.json'), 'w')
    f.write(
        json.dumps(
            {
                'res': res,
                'out': out_timings,
                'in': in_timings
            }
        )
    )
    f.close()

    # Plot
    out_file_path, in_file_path = _plot(results_dir_path, out_timings,
                                        in_timings)

    # Print
    print 'Look for %s and %s.' % (out_file_path, in_file_path)


#
# Tasks
#

@ice.ParallelTask
def copy_key(hosts):
    """Necessary first step, copies SSH keys to all instances."""
    fab.put(os.path.expanduser('~/.ssh/id_rsa'), '/home/ec2-user/.ssh')
    fab.put(os.path.expanduser('~/.ssh/id_rsa.pub'), '/home/ec2-user/.ssh')
    fab.run('chmod 600 ~/.ssh/id_rsa*')


@ice.Task
def ping(hosts, sent_bytes_amt=DEF_SENT_BYTES_AMT):
    """Sends a big packet from each host to each other host."""
    reg_ex = re.compile(r'([0-9\.]+) MB\/s', re.MULTILINE)

    with fab.settings(warn_only=True):
        out_timings = []
        in_timings = []

        for hs, inst in hosts.items():
            if hs == fab.env.host_string:
                continue

            # Get address
            net = inst.networks[0]
            addr = net['addr'].replace('/20', '')

            # Run transfer
            cmd = 'sudo dd if=/dev/xvda1 bs=1024 count={:d}'.format(
                sent_bytes_amt / 1024
            )
            cmd += ' | ssh -o "StrictHostKeyChecking no" {0:s} "{1:s}"'.format(
                addr, 'dd of=/dev/null'
            )
            output = fab.run(cmd)

            # Clean up
            fab.run('rm ~/test', quiet=True)

            # Get the rate
            matches = re.findall(reg_ex, output)
            if matches is not None and len(matches) == 2:
                out_timings.append(float(matches[0]))
                in_timings.append(float(matches[1]))

        print 'Host %s done!' % fab.env.host_string
        return out_timings, in_timings


#
# Helpers
#

def _plot(results_dir_path, out_timings, in_timings, file_name_suffix=None):
    # File paths
    if file_name_suffix is not None:
        out_file_path = 'out_timings-%s.png' % file_name_suffix
        in_file_path = 'in_timings-%s.png' % file_name_suffix
    else:
        out_file_path = 'out_timings.png'
        in_file_path = 'in_timings.png'
    out_file_path = os.path.join(results_dir_path, out_file_path)
    in_file_path = os.path.join(results_dir_path, in_file_path)

    # Out
    plt.xlabel('MB/s')
    plt.ylabel('Probability')
    plt.subplots_adjust(left=0.15)
    plt.title('Out dd speed, #%d samples' % len(out_timings))
    plt.hist(
        out_timings, 50, alpha=0.5,
        label='Out dd speed'
    )
    plt.savefig(out_file_path)
    plt.close()

    # In
    plt.xlabel('MB/s')
    plt.ylabel('Probability')
    plt.subplots_adjust(left=0.15)
    plt.title('In dd speed, #%d samples' % len(in_timings))
    plt.hist(
        in_timings, 50, alpha=0.5,
        label='In dd speed'
    )
    plt.savefig(in_file_path)
    plt.close()

    return out_file_path, in_file_path
