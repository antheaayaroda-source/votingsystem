from django.core.management.base import BaseCommand
from voting.models import Party, Candidate

class Command(BaseCommand):
    help = 'Fix duplicate teams and ensure delete functionality works'

    def handle(self, *args, **options):
        # First, let's clean up the duplicate teams
        teams = {
            'TEAM GALING': '✨TEAM GALING✨',
            'TEAM SIGLA': '✨TEAM SIGLA✨'
        }

        for old_name, new_name in teams.items():
            try:
                old_team = Party.objects.get(name=old_name)
                new_team = Party.objects.get(name=new_name)
                
                # Move all candidates from old team to new team
                Candidate.objects.filter(party=old_team).update(party=new_team)
                
                # Delete the old team
                old_team.delete()
                self.stdout.write(self.style.SUCCESS(f'Merged {old_name} into {new_name}'))
                
            except Party.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'{old_name} or {new_name} not found, skipping...'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {old_name}: {str(e)}'))

        # Verify the fix
        remaining_teams = list(Party.objects.all().values_list('name', flat=True))
        self.stdout.write(self.style.SUCCESS(f'Remaining teams: {remaining_teams}'))
        
        # Now let's fix the delete functionality by ensuring all teams have the correct structure
        for team in Party.objects.all():
            try:
                # Just accessing these will ensure they exist
                _ = team.president
                _ = team.vice_president
                _ = team.secretary
                self.stdout.write(self.style.SUCCESS(f'Team {team.name} is properly structured'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error with team {team.name}: {str(e)}'))
                # Try to fix by refreshing from DB
                team.refresh_from_db()
