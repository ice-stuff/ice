"""A test experiment"""
import os
import re
import matplotlib.pyplot as plt
from fabric import api as fab
import ice
import json

#
# Data
#

REG_EX = re.compile(r'([0-9\.]+) MB\/s', re.MULTILINE)
SENT_BYTES_AMT = 536870912
# SENT_BYTES_AMT = 1024
RESULTS_DIR_PATH = os.path.expanduser(
    '~/di_dev/Thesis/Results/Tutorial/%s' % str(SENT_BYTES_AMT)
)
if not os.path.isdir(RESULTS_DIR_PATH):
    os.mkdir(RESULTS_DIR_PATH)

#
# Runners
#


@ice.Runner
def re_plot(hosts):
    """Re-plots the graphs."""
    data_file_path = os.path.join(RESULTS_DIR_PATH, 'data.json')
    if not os.path.isfile(data_file_path):
        print 'ERROR: File `%s` not found!' % data_file_path
        return

    # Read file
    f = open(data_file_path)
    d = json.loads(f.read())
    f.close()

    # Re-plot
    out_file_path, in_file_path = _plot(d['out'], d['in'])

    # Print
    print 'Look for %s and %s.' % (out_file_path, in_file_path)


@ice.Runner
def run(hosts):
    """Runs the tutorial."""
    # Copy keys
    fab.execute(copy_key, hosts)

    # Experimentation
    in_timings = []
    out_timings = []
    res = fab.execute(ping, hosts)
    for key, ret_val in res.items():
        ot, it = ret_val
        out_timings += ot
        in_timings += it

    # Write data
    f = open(os.path.join(RESULTS_DIR_PATH, 'data.json'), 'w')
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
    out_file_path, in_file_path = _plot(out_timings, in_timings)

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
def ping(hosts):
    """Sends a big packet from each host to each other host."""
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
                SENT_BYTES_AMT / 1024
            )
            cmd += ' | ssh -o "StrictHostKeyChecking no" {0:s} "{1:s}"'.format(
                addr, 'dd of=~/test'
            )
            output = fab.run(cmd)

            # Clean up
            fab.run('rm ~/test', quiet=True)

            # Get the rate
            matches = re.findall(REG_EX, output)
            if matches is not None and len(matches) == 2:
                out_timings.append(float(matches[0]))
                in_timings.append(float(matches[1]))

        print 'Host %s done!' % fab.env.host_string
        return (out_timings, in_timings)


#
# Helpers
#

def _plot(out_timings, in_timings, file_name_suffix=None):
    # File paths
    if file_name_suffix is not None:
        out_file_path = 'out_timings-%s.png' % file_name_suffix
        in_file_path = 'in_timings-%s.png' % file_name_suffix
    else:
        out_file_path = 'out_timings.png'
        in_file_path = 'in_timings.png'
    out_file_path = os.path.join(RESULTS_DIR_PATH, out_file_path)
    in_file_path = os.path.join(RESULTS_DIR_PATH, in_file_path)

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

    return (out_file_path, in_file_path)
