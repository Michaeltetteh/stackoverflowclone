from django.core.management import BaseCommand
from qanda.service import elasticsearch
from qanda.models import Question

class Command(BaseCommand):
    help = 'load all questions into Elasticsearch'

    def handle(self, *args, **options):
        querset = Question.objects.all()
        all_loaded = elasticsearch.bulk_load(querset)
        if all_loaded:
            self.stdout.write(self.style.SUCCESS(
                'Done loading all questions into elasticsearch'
            ))
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Some questions not loaded Successfully. \n See logged error'
                )
            )

