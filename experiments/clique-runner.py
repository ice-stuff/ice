#!/usr/bin/env python
import sys
import os
import argparse
import datetime

from ice import api
from ice import logging




#
# Global
#

# Logging debug
logger = logging.get_logger('ice')
logger.setLevel(logging.DEBUG)

# Current sessions
current_session = None

# EC2 reservation
ec2_reservation = None


#
# Functions
#

def _get_argument_parser():
    """
    :rtype: argparse.ArgumentParser
    """
    ret_val = argparse.ArgumentParser()
    ret_val.add_argument(
        '-n', dest='instances_amt', type=int, default=2,
        metavar='<Amount of instances to launch>'
    )
    ret_val.add_argument('-i', metavar='<AMI Id>', dest='ami_id')
    ret_val.add_argument('-t', metavar='<Type>', dest='flavor')
    ret_val.add_argument('-c', metavar='<Cloud Id>', dest='cloud_id')
    ret_val.add_argument(
        '-d', dest='results_dir_path', type=None,
        metavar='<Path of directory to put results>'
    )
    return ret_val


def _launch_instances(instances_amt=10, flavor=None, ami_id=None,
                      cloud_id=None):
    global current_session, ec2_reservation, logger

    # Start session
    current_session = api.session.start()
    if current_session is None:
        logger.error('Failed to start session!')
        return False
    logger.info('session id = {0.id:s}.'.format(current_session))

    # Run EC2 instances
    logger.info('Spawning VMs...')
    ec2_reservation = api.ec2.create(
        instances_amt,
        flavor=flavor,
        ami_id=ami_id,
        cloud_id=cloud_id
    )
    if ec2_reservation is None:
        logger.error('Failed to run EC2 instances!')
        return False
    logger.info('EC2 reservation id = {0.id:s}.'.format(ec2_reservation))

    # Wait for EC2 instances
    logger.info('Waiting for EC2 instances to come up...')
    ret_val = api.ec2.wait(120)
    if ret_val:
        logger.info('All EC2 instances came up.')
    else:
        logger.error(
            'Timeout while waiting for the EC2 instances to come up!'
        )
        return False

    # Wait for them to join the pool
    logger.info('Waiting for instances to join the pool...')
    ret_val = api.instances.wait(instances_amt, 600)
    if ret_val:
        logger.info('{0:d} instances joined the pool.'.format(instances_amt))
    else:
        logger.error(
            'Timeout while waiting for the instances to join the pool!'
        )
        return False

    return True


def _make_dir_path(results_dir_path=None, flavor=None, ami_id=None,
                   cloud_id=None):
    # Path prefix
    if results_dir_path is None:
        ret_val = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'results'
        )
    else:
        ret_val = results_dir_path

    # Cloud?
    if cloud_id is not None:
        ret_val = os.path.join(ret_val, cloud_id)
    # Flavor?
    if flavor is not None:
        ret_val = os.path.join(ret_val, flavor)
    # AMI Id?
    if ami_id is not None:
        ret_val = os.path.join(ret_val, ami_id)

    # Add timestamp
    curr_dt = datetime.datetime.now()
    ret_val = os.path.join(
        ret_val,
        '{0.year:04d}{0.month:02d}{0.day:02d}'.format(curr_dt),
        '{0.hour:02d}{0.minute:02d}{0.second:02d}'.format(curr_dt)
    )

    # Make path if it does not exist
    if not os.path.isdir(ret_val):
        os.makedirs(ret_val)

    return ret_val


def _run(results_dir_path=None):
    global logger

    # Load the experiment
    logger.info('Loading the experiment...')
    exp = api.experiment.load(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'tutorial.py'
        )
    )

    # Run the experiment
    logger.info('Running the experiment...')
    if exp is None:
        logger.error('Failed to load experiment!')
        return False
    exp.run('run', [results_dir_path])

    return True


def _clean():
    global logger, current_session, ec2_reservation

    if current_session is not None:
        # Close the session
        logger.info('Closing session.')
        api.session.close(current_session)

    if ec2_reservation is not None:
        # Destroy EC2 instances
        instance_ids = []
        for inst in ec2_reservation.instances:
            instance_ids.append(inst.id)
        logger.info('Destroying EC2 instances...')
        api.ec2.destroy(instance_ids)


#
# Main caller
#

if __name__ == '__main__':
    # Parse arguments
    parser = _get_argument_parser()
    args = parser.parse_args()

    try:
        # Spawn VMs
        logger.info(
            'n={0.instances_amt:d}, flavor={0.flavor:s},'.format(args)
            + ' ami_id={0.ami_id:s}, cloud_id={0.cloud_id:s}.'.format(args)
        )
        result = _launch_instances(
            args.instances_amt, args.flavor, args.ami_id, args.cloud_id
        )

        # Run
        if result:
            # Get results directory path
            results_dir_path = _make_dir_path(
                args.results_dir_path, args.flavor, args.ami_id, args.cloud_id
            )
            logger.info('results_dir_path={0}.'.format(results_dir_path))

            # Run
            result = _run(results_dir_path)
    except Exception as ex:
        logger.error('Exception: {0:s}'.format(str(ex)))
        result = False

    # Clean
    _clean()

    # Exit code
    if not result:
        sys.exit(1)
    sys.exit(0)
