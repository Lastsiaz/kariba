from django.core.management.base import BaseCommand
import csv
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Convert existing training_data.csv from old format to new format'

    def handle(self, *args, **options):
        try:
            models_dir = os.path.join(settings.BASE_DIR, 'models', 'sentiment_analysis')
            training_file = os.path.join(models_dir, 'training_data.csv')
            backup_file = os.path.join(models_dir, 'training_data_backup.csv')
            
            if not os.path.exists(training_file):
                self.stdout.write(
                    self.style.ERROR(f'Training data file not found: {training_file}')
                )
                return
            
            # Create backup
            import shutil
            shutil.copy2(training_file, backup_file)
            self.stdout.write(
                self.style.SUCCESS(f'Created backup: {backup_file}')
            )
            
            # Read old format and convert
            converted_data = []
            with open(training_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    text = row.get('tweets_descriptions', '').strip()
                    sentiment = row.get('tweets_classification', '').strip().lower()
                    
                    if text and sentiment:
                        converted_data.append([text, sentiment])
            
            # Write new format
            with open(training_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['text', 'sentiment'])
                writer.writerows(converted_data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully converted {len(converted_data)} records to new format')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error converting training data: {str(e)}')
            ) 