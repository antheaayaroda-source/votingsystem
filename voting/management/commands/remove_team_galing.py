from django.core.management.base import BaseCommand
from django.db.models import Q

class Command(BaseCommand):
    help = 'Remove any Party with name or team_name matching TEAM GALING and delete its candidates.'

    def handle(self, *args, **options):
        from voting.models import Party, Candidate

        qs = Party.objects.filter(Q(team_name__iexact='TEAM GALING') | Q(name__iexact='TEAM GALING'))
        if not qs.exists():
            self.stdout.write(self.style.SUCCESS('No PARTY matching "TEAM GALING" found.'))
            return

        total_deleted = 0
        for p in qs:
            self.stdout.write(f'Found Party: id={p.id}, name="{p.name}", team_name="{p.team_name}"')
            cand_qs = Candidate.objects.filter(party=p)
            cand_count = cand_qs.count()
            if cand_count:
                deleted = cand_qs.delete()
                self.stdout.write(f' - Deleted {deleted[0]} candidate(s)')
                total_deleted += deleted[0]
            p.delete()
            self.stdout.write(f' - Deleted party id={p.id}')

        self.stdout.write(self.style.SUCCESS(f'Deletion complete. Total candidates deleted: {total_deleted}.'))
