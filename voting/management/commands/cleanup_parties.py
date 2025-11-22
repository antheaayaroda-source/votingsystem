from django.core.management.base import BaseCommand
from voting.models import Party, Candidate

class Command(BaseCommand):
    help = 'Clean up duplicate and empty parties'

    def handle(self, *args, **options):
        # Get all parties
        parties = list(Party.objects.all())
        party_names = {}
        
        # Track parties to delete
        to_delete = []
        
        for party in parties:
            # Clean up the party name for comparison
            clean_name = party.name.strip().replace('✨', '').strip().upper()
            
            # If we've seen this name before
            if clean_name in party_names:
                # Keep the one with emojis if possible
                if '✨' in party.name:
                    to_delete.append(party_names[clean_name]['party'])
                    party_names[clean_name] = {'party': party, 'count': 0}
                else:
                    to_delete.append(party)
            else:
                party_names[clean_name] = {'party': party, 'count': 0}
            
            # Count candidates for this party
            count = Candidate.objects.filter(party=party).count()
            if count == 0 and party not in to_delete:
                to_delete.append(party)
        
        # Delete the parties
        if to_delete:
            deleted_count = len(to_delete)
            for party in to_delete:
                self.stdout.write(f'Deleting empty/duplicate party: {party.name} (ID: {party.id})')
                party.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} parties'))
        else:
            self.stdout.write('No empty or duplicate parties found to delete')
