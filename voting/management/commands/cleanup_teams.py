from django.core.management.base import BaseCommand
from voting.models import Party

class Command(BaseCommand):
    help = 'Remove duplicate teams (non-emoji versions)'

    def handle(self, *args, **options):
        # Teams to keep (with emojis)
        teams_to_keep = ['✨TEAM GALING✨', '✨TEAM SIGLA✨']
        
        # Teams to remove (without emojis)
        teams_to_remove = ['TEAM GALING', 'TEAM SIGLA']
        
        # Delete the duplicate teams
        deleted_count, _ = Party.objects.filter(name__in=teams_to_remove).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {deleted_count} duplicate teams')
        )
        
        # Show remaining teams
        remaining_teams = list(Party.objects.all().values_list('name', flat=True))
        self.stdout.write(f'Remaining teams: {remaining_teams}')
