# pylint: disable=no-member,line-too-long

import base64

import six

from nacl.secret import SecretBox

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Loads content from incremental backups of data content.'

    def add_arguments(self, parser):
        parser.add_argument('file',
                            nargs='+',
                            type=str,
                            help='Backup file to decrypt')

    def handle(self, *args, **options):
        key = base64.b64decode(settings.SIMPLE_BACKUP_KEY) # getpass.getpass('Enter secret backup key: ')

        for encrypted_file in  options['file']:
            box = SecretBox(key)

            with open(encrypted_file, 'rb') as backup_file:
                encrypted_content = backup_file.read()

                content = box.decrypt(encrypted_content)

                with open(encrypted_file.replace('.encrypted', ''), 'wb') as output:
                    output.write(content)

                    six.print_('Decrypted %s' % encrypted_file.replace('.encrypted', ''))
