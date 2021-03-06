from django.core.management.base import BaseCommand, CommandError
from marine_parts.apps.categorizer.categorizer import exec_loader

class Command(BaseCommand):
    help = 'Load products from json scraped data'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+')

        parser.add_argument(
            '--log',
            action='store_true',
            dest='log',
            help='Show log messages.'
        )

        parser.add_argument(
            '--cat_base',
            action='store',
            dest='cat_base',
            default="Brands",
            help='Category where the created products are put.'
        )


    def handle(self, *args, **options):
        total = 0

        cat_base = options['cat_base']
        self.stdout.write(self.style.WARNING('Using base category: %s.' % cat_base))

        verbosity = options['log']
        if verbosity:
            self.stdout.write(self.style.WARNING('Log mode on.'))

        for filepath in options['filepaths']:
            self.stdout.write('Processing file %s. Please wait...' % filepath)
            try:
                nro = self.ejec(filepath, cat_base, verbosity)
            except CommandError as ce:
                self.stderr.write(self.style.ERROR(ce.message.decode('utf-8') + ' Skipping...'))
                continue

            self.stdout.write(self.style.SUCCESS('%s products were created in DB from %s' % (nro, filepath)))

            total += nro

        if total > 0:
            self.stdout.write(self.style.SUCCESS('Total products created: %s' % total))
        else:
            self.stdout.write(self.style.WARNING('No products were created'))


    def ejec(self, filepath, cat_base, verbosity):
        try:
            nro = exec_loader(filepath, cat_base, verbosity)
        except Exception:
            import sys, traceback
            exc_info = sys.exc_info()
            traceback.print_tb(exc_info[2])
            print(exc_info[1])
            raise CommandError('An error occurred while processing this file: %s' % filepath)

        return nro