#!/usr/bin/env python3
import os
import sys

# Ensure working directory is project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')
import django
django.setup()

from django.db.models import Q
from voting.models import Party, Candidate

def main():
    qs = Party.objects.filter(Q(team_name__iexact='TEAM GALING') | Q(name__iexact='TEAM GALING'))
    if not qs.exists():
        print('No PARTY matching "TEAM GALING" (by name or team_name) found.')
        return

    for p in qs:
        print(f'Found Party: id={p.id}, name="{p.name}", team_name="{p.team_name}"')
        cand_qs = Candidate.objects.filter(party=p)
        cand_count = cand_qs.count()
        print(f' - Candidates to delete: {cand_count}')
        deleted_cands = cand_qs.delete()
        print(f' - Deleted candidates: {deleted_cands[0]}')
        p.delete()
        print(f' - Deleted party id={p.id}')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error running deletion script:', e)
        sys.exit(1)
