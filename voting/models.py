from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Position(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    max_vote = models.IntegerField(default=1)
    def __str__(self):
        return self.name

class Party(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    # Team information
    team_name = models.CharField(max_length=100, blank=True, null=True, help_text="Team name (e.g., Team Galing, Team Sigla)")
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='parties/', blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    leader = models.CharField(max_length=100, blank=True, null=True)
    rules = models.TextField(blank=True, null=True, help_text="Team rules and guidelines")
    
    # Candidates for the team
    president = models.ForeignKey('Candidate', related_name='president_of', on_delete=models.SET_NULL, null=True, blank=True)
    vice_president = models.ForeignKey('Candidate', related_name='vice_president_of', on_delete=models.SET_NULL, null=True, blank=True)
    secretary = models.ForeignKey('Candidate', related_name='secretary_of', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Parties'
    
    def __str__(self):
        return self.name
    
    def get_team_members(self):
        """Return a dictionary of team members by position"""
        return {
            'President': self.president,
            'Vice President': self.vice_president,
            'Secretary': self.secretary
        }

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    votes = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.name} ({self.position.name})"

class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    grade_level = models.CharField(max_length=50, blank=True, null=True)
    strand = models.CharField(max_length=50, blank=True, null=True)
    id_number = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    has_voted = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.voter.user.username} -> {self.candidate.name}"

@receiver(post_save, sender=User)
def create_voter(sender, instance, created, **kwargs):
    if created:
        Voter.objects.create(user=instance)
