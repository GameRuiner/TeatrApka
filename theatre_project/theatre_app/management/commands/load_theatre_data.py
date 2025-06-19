import json
import os
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date, parse_time
from theatre_app.models import Theatre, Performance

class Command(BaseCommand):
    help = 'Load theatre data from JSON files'
    
    def add_arguments(self, parser):
        parser.add_argument('json_dir', type=str, help='Directory containing JSON files')
    
    def handle(self, *args, **options):
        json_dir = options['json_dir']
        
        if not os.path.exists(json_dir):
            self.stdout.write(self.style.ERROR(f'Directory {json_dir} does not exist'))
            return
        
        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                self.load_json_file(os.path.join(json_dir, filename))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded all theatre data'))
    
    def load_json_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        for item in data:
            # Get or create theatre
            # theatre_name = item.get('place', 'Unknown Theatre')
            # theatre, created = Theatre.objects.get_or_create(name=theatre_name)
            
            # if created:
            #     self.stdout.write(f'Created theatre: {theatre_name}')
            
            # Parse date and time
            date_str = item.get('date')
            time_str = item.get('time')
            
            if not date_str or not time_str:
                self.stdout.write(self.style.WARNING(f'Skipping item with missing date/time: {item}'))
                continue
            
            date_obj = parse_date(date_str)
            time_obj = parse_time(time_str)
            
            if not date_obj or not time_obj:
                self.stdout.write(self.style.WARNING(f'Invalid date/time format: {date_str}/{time_str}'))
                continue
            
            # Create or update performance
            performance, created = Performance.objects.get_or_create(
                title=item.get('title', 'Untitled'),
                # theatre=theatre,
                date=date_obj,
                time=time_obj,
                # defaults={
                #     'status': item.get('status', 'KUP BILET'),
                # }
            )
            
            # if created:
            #     self.stdout.write(f'Created performance: {performance.title} at {theatre_name}')
            # else:
            #     # Update status if it changed
            #     if performance.status != item.get('status', 'KUP BILET'):
            #         performance.status = item.get('status', 'KUP BILET')
            #         performance.save()
            #         self.stdout.write(f'Updated performance: {performance.title}')
