from django.core.management.base import BaseCommand
from voting.models import Candidate

class Command(BaseCommand):
    help = 'Remove all candidates from the database'

    def handle(self, *args, **options):
        # Get the count before deletion
        count = Candidate.objects.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No candidates found in the database.'))
            return

        # Ask for confirmation
        confirm = input(f'Are you sure you want to delete ALL {count} candidates? This action cannot be undone. (yes/no): ')
        
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.WARNING('Operation cancelled. No candidates were deleted.'))
            return

        # Delete all candidates
        deleted = Candidate.objects.all().delete()
        
        # The delete() method returns a tuple: (number_deleted, {model_name: number_deleted})
        if deleted[0] > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted[0]} candidates from the database.')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No candidates were deleted.')
            )
