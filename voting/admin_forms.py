from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Candidate, Party, Voter, Position

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'position', 'party', 'photo', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter candidate name',
                'required': True
            }),
            'position': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'party': forms.Select(attrs={
                'class': 'form-select'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter candidate biography (optional)'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ['name', 'logo', 'description', 'founded_date', 'leader']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter party name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter party description (optional)'
            }),
            'founded_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'leader': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of party leader (optional)'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['first_name', 'middle_name', 'last_name', 'id_number', 'grade_level', 'strand', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'grade_level': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'strand': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'description', 'max_vote']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., President, Vice President',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description of the position (optional)'
            }),
            'max_vote': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1,
                'required': True
            })
        }

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserEditForm(UserChangeForm):
    password = None  # Remove the password field
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
