from django.core.management.base import BaseCommand
from recommendations.kmeans import generate_recommendations

class Command(BaseCommand):
    help = 'Generate recommendations for users using K-means clustering'

    def handle(self, *args, **options):
        self.stdout.write('Generating recommendations...')
        generate_recommendations()
        self.stdout.write(self.style.SUCCESS('Successfully generated recommendations')) 