# pylint: disable=line-too-long

from django.conf import settings
from django.core.checks import Warning, register # pylint: disable=redefined-builtin

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

@register()
def check_backup_parameters(app_configs, **kwargs): # pylint: disable=unused-argument
    errors = []

    if hasattr(settings, 'SIMPLE_BACKUP_DESTINATIONS') is False:
        warning = Warning('SIMPLE_BACKUP_DESTINATIONS parameter not defined', hint='Update configuration to include SIMPLE_BACKUP_DESTINATIONS.', obj=None, id='simple_backup.W001')
        errors.append(warning)
    else:
        for destination in settings.SIMPLE_BACKUP_DESTINATIONS:
            destination_url = urlparse(destination)

            if destination_url.scheme == 'file':
                pass # Check for folder?
            elif destination_url.scheme == 'dropbox':
                pass # Check for accessible folder?
            elif destination_url.scheme == 's3':
                if hasattr(settings, 'SIMPLE_BACKUP_AWS_ACCESS_KEY_ID') is False:
                    warning = Warning('SIMPLE_BACKUP_AWS_ACCESS_KEY_ID parameter not defined', hint='Update configuration to include SIMPLE_BACKUP_AWS_ACCESS_KEY_ID.', obj=None, id='simple_backup.W010')
                    errors.append(warning)

                if hasattr(settings, 'SIMPLE_BACKUP_AWS_SECRET_ACCESS_KEY') is False:
                    warning = Warning('SIMPLE_BACKUP_AWS_SECRET_ACCESS_KEY parameter not defined', hint='Update configuration to include SIMPLE_BACKUP_AWS_SECRET_ACCESS_KEY.', obj=None, id='simple_backup.W011')
                    errors.append(warning)

                if hasattr(settings, 'SIMPLE_BACKUP_AWS_REGION') is False:
                    warning = Warning('SIMPLE_BACKUP_AWS_REGION parameter not defined', hint='Update configuration to include SIMPLE_BACKUP_AWS_REGION.', obj=None, id='simple_backup.W012')
                    errors.append(warning)

    if hasattr(settings, 'SIMPLE_BACKUP_KEY') is False:
        warning = Warning('SIMPLE_BACKUP_KEY parameter not defined', hint='Update configuration to include SIMPLE_BACKUP_KEY.', obj=None, id='simple_backup.W002')
        errors.append(warning)

    return errors
