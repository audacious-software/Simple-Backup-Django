# pylint: disable=no-member,line-too-long,superfluous-parens

from builtins import str # pylint: disable=redefined-builtin

import datetime

import pytz

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand

from ...decorators import handle_lock

class Command(BaseCommand):
    help = 'Executes sequential incremental backups.'

    def add_arguments(self, parser):
        parser.add_argument('--start-date',
                            type=str,
                            dest='start_date',
                            required=True,
                            help='Start of date range for incremental backup')

        parser.add_argument('--end-date',
                            type=str,
                            dest='end_date',
                            required=True,
                            help='End of date range for incremental backup')

        parser.add_argument('--window-days',
                            dest='window_days',
                            default=7,
                            type=int,
                            help='Number of days for each backup job')

        parser.add_argument('--filter-sensitive-data',
                            dest='filter_sensitive',
                            action='store_true',
                            help='Filter sensitive data from the backup data points written')


    @handle_lock
    def handle(self, *args, **options):
        here_tz = pytz.timezone(settings.TIME_ZONE)

        components = options['start_date'].split('-')

        start_date = datetime.datetime(int(components[0]), int(components[1]), int(components[2]), 0, 0, 0, 0, here_tz).date()

        components = options['end_date'].split('-')

        end_date = datetime.datetime(int(components[0]), int(components[1]), int(components[2]), 0, 0, 0, 0, here_tz).date()

        while start_date <= end_date:
            local_end_date = start_date + datetime.timedelta(days=(options['window_days'] - 1))

            local_end_date = min(local_end_date, end_date)

            arguments = [
                '--start-date',
                start_date.isoformat(),
                '--end-date',
                local_end_date.isoformat()
            ]

            if options['filter_sensitive'] is not None and options['filter_sensitive'] is not False:
                arguments.append('--filter-sensitive-data')

            management.call_command('incremental_backup', *arguments)

            start_date = local_end_date + datetime.timedelta(days=1)
