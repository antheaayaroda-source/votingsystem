from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voting.models import Party, Position, Candidate, Voter

class Command(BaseCommand):
    help = 'Set up the teams and their candidates'

    def handle(self, *args, **options):
        # Create positions if they don't exist
        president_pos, _ = Position.objects.get_or_create(name='President')
        vice_president_pos, _ = Position.objects.get_or_create(name='Vice President')
        secretary_pos, _ = Position.objects.get_or_create(name='Secretary')

        # Create or get the teams
        team_galing, _ = Party.objects.get_or_create(
            team_name='TEAM GALING',
            defaults={'name': 'TEAM GALING'}
        )
        
        team_sigla, _ = Party.objects.get_or_create(
            team_name='TEAM SIGLA',
            defaults={'name': 'TEAM SIGLA'}
        )

        # Create or get candidates for TEAM GALING
        joshua, _ = Candidate.objects.get_or_create(
            name='Joshua Montes',
            defaults={
                'position': president_pos,
                'party': team_galing
            }
        )
        
        justin, _ = Candidate.objects.get_or_create(
            name='Justin Quino',
            defaults={
                'position': vice_president_pos,
                'party': team_galing
            }
        )
        
        atasha, _ = Candidate.objects.get_or_create(
            name='Atasha Brigo',
            defaults={
                'position': secretary_pos,
                'party': team_galing
            }
        )

        # Create or get candidates for TEAM SIGLA
        jeyn, _ = Candidate.objects.get_or_create(
            name='Jeyn Santos',
            defaults={
                'position': president_pos,
                'party': team_sigla
            }
        )
        
        joseph, _ = Candidate.objects.get_or_create(
            name='Joseph Garcia',
            defaults={
                'position': vice_president_pos,
                'party': team_sigla
            }
        )
        
        zereyn, _ = Candidate.objects.get_or_create(
            name='Zereyn Hapis',
            defaults={
                'position': secretary_pos,
                'party': team_sigla
            }
        )

        # Update team assignments
        team_galing.president = joshua
        team_galing.vice_president = justin
        team_galing.secretary = atasha
        team_galing.save()

        team_sigla.president = jeyn
        team_sigla.vice_president = joseph
        team_sigla.secretary = zereyn
        team_sigla.save()

        self.stdout.write(self.style.SUCCESS('Successfully set up teams and candidates'))
