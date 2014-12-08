#!/usr/bin/env python
import sys
import os

from ice import api
from ice import logging


#
# Configuration
#

INSTANCES_AMT = 10


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

def _run():
    global current_session, ec2_reservation, logger

    # Start session
    current_session = api.session.start()
    if current_session is None:
        logger.error('Failed to start session!')
        return False
    logger.info('session id = {0.id:s}.'.format(current_session))

    # Run EC2 instances
    ec2_reservation = api.ec2.create(INSTANCES_AMT)
    if ec2_reservation is None:
        logger.error('Failed to run EC2 instances!')
        return False
    logger.info('EC2 reservation id = {0.id:s}.'.format(ec2_reservation))
    logger.info('Waiting for EC2 instances to come up...')
    api.ec2.wait()

    # Wait for them to join the pool
    logger.info('Waiting for instances to join the pool...')
    api.instances.wait(INSTANCES_AMT)

    # Run the experiment
    logger.info('Running the experiment...')
    exp = api.experiment.load(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'tutorial.py'
        )
    )
    if exp is None:
        logger.error('Failed to load experiment!')
        return False
    exp.run()

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
    # Run
    try:
        result = _run()
    except Exception as ex:
        logger.error('Exception: {0:s}'.format(str(ex)))
        result = False

    # Clean
    _clean()

    # Exit code
    if not result:
        sys.exit(1)
    sys.exit(0)
