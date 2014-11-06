from iCE.config import Configuration
from iCE.rest_api.domain import *


#
# Externals
#

def _apply_mongodb_settings(settings):
    cfg = Configuration.get_configuration()
    settings['MONGO_HOST'] = cfg.get_var('mongodb', 'host', 'localhost')
    settings['MONGO_PORT'] = cfg.get_int('mongodb', 'port', 27017)
    settings['MONGO_USERNAME'] = cfg.get_var('mongodb', 'username', '')
    settings['MONGO_PASSWORD'] = cfg.get_var('mongodb', 'password', '')
    settings['MONGO_DBNAME'] = cfg.get_var('mongodb', 'db_name', 'iCE')


def _apply_redis_settings(settings):
    pass


#
# Domain and validation
#

def _apply_domain_settings(settings):
    cfg = Configuration.get_configuration()

    # Version of the API
    settings['API_VERSION'] = 'v1'

    # Domains
    settings['DOMAIN'] = {
        InstancesDomain.ENDPOINT: InstancesDomain.get_config()
    }

    # Disable HATEOAS
    # settings['HATEOAS'] = False

    # Debug mode
    settings['DEBUG'] = cfg.get_bool('ice', 'debug', False)


#
# Authentication
#

def _apply_authentication_settings(settings):
    pass


#
# API limiting
#

def _apply_limiting_settings(settings):
    pass


#
# Main function
#

def get_settings():
    settings = {}

    # Externals
    _apply_mongodb_settings(settings)
    _apply_redis_settings(settings)

    # Domain and validation
    _apply_domain_settings(settings)

    # Authentication
    _apply_authentication_settings(settings)

    # API limiting
    _apply_limiting_settings(settings)

    return settings
