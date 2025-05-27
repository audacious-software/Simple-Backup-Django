# pylint: disable=no-member,line-too-long

import importlib
import os
import sys
import traceback
import urllib

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Executes sequential incremental backups.'

    def handle(self, *args, **options): # pylint: disable=too-many-locals
        if '--help' in args or len(args) < 3:
            print('Usage: manual_sync.py <source> <destination>')
            print('')
            print('         <source>: Source of files in URL format: e.g. s3://my-s3-bucket/')
            print('    <destination>: Files\' destination  in URL format: e.g. google-drive://GOOGLE-FOLDER-ID/')
            print('')

            sys.exit(0)

        source = None
        destination = None

        for arg in args[1:]:
            if source is None:
                source = arg
            elif destination is None:
                destination = arg

        if None in (source, destination):
            print('Missing source or destination parameter. Use --help argument for details.')
            sys.exit(1)

        source_url = urllib.parse.urlparse(source)
        destination_url = urllib.parse.urlparse(destination)

        source_module = importlib.import_module('storage.%s' % source_url.scheme.replace('-', '_'))
        destination_module = importlib.import_module('storage.%s' % destination_url.scheme.replace('-', '_'))

        try:
            source_list = source_module.list_files(source)
        except: # pylint: disable=bare-except
            print('Error fetching files from %s.' % source)
            traceback.print_exc()

            sys.exit(1)

        try:
            request_list = destination_module.create_sync_request(source_list, destination)
        except: # pylint: disable=bare-except
            print('Error building sync request files from %s.' % destination)
            traceback.print_exc()

            sys.exit(1)

        request_index = 1

        for request_item in request_list:
            file_content, file_type = source_module.fetch_content(source, request_item)

            try:
                if destination_module.upload_content(destination, request_item, file_content, file_type) is not None:
                    print('Synced %s... (%s of %s)' % (request_item, request_index, len(request_list)))
                else:
                    print('Error syncing %s... (%s of %s)' % (request_item, request_index, len(request_list)))
            except: # pylint: disable=bare-except
                print('Error syncing %s from %s to %s.' % (request_item, source_url.scheme, destination_url.scheme))
                traceback.print_exc()

                sys.exit(1)

            request_index += 1

if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()

    command = Command()

    sys.path.insert(0, os.getcwd())

    importlib.invalidate_caches()

    parser = command.create_parser('', 'manual_sync')
    command.add_arguments(parser)

    command.handle(*sys.argv, **{})
