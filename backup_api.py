from __future__ import print_function

import bz2
import gc
import io
import logging
import os
import sys
import tempfile

from django.conf import settings
from django.core import management
from django.utils.text import slugify

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

def incremental_backup(parameters): # pylint: disable=unused-argument
    to_transmit = []

    # Dump full content of these models. No incremental backup here.

    dumpdata_apps = (
        'auth',
    )

    prefix = 'simple_backup_' + settings.ALLOWED_HOSTS[0]

    backup_staging = tempfile.gettempdir()

    try:
        backup_staging = settings.SIMPLE_BACKUP_STAGING_DESTINATION
    except AttributeError:
        pass

    for app in dumpdata_apps:
        logger.info('[simple_backup] Backing up %s...', app)
        sys.stdout.flush()

        buf = io.StringIO()
        management.call_command('dumpdata', app, stdout=buf)
        buf.seek(0)

        database_dump = buf.read()

        buf = None

        gc.collect()

        compressed_str = bz2.compress(database_dump.encode('utf-8'))

        database_dump = None

        gc.collect()

        filename = prefix + '_' + slugify(app) + '.json-dumpdata.bz2'

        path = os.path.join(backup_staging, filename)

        with io.open(path, 'wb') as fixture_file:
            fixture_file.write(compressed_str)

        to_transmit.append(path)

    return to_transmit
