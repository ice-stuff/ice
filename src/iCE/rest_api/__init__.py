from eve import Eve
from . import settings
from .validation import MyValidator

# Setup the application
_settings = settings.get_settings()
app = Eve(settings=_settings, validator=MyValidator)
