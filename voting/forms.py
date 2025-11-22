from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Position, Candidate, Party

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Username',
        'class': 'input-box'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'input-box'
    }))



class RegistrationForm(UserCreationForm):
    # User account fields
    username = forms.CharField(
        label='Student ID',
        help_text='Enter your student ID number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Student ID',
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    first_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={
            'placeholder': 'First name',
            'class': 'form-control',
            'autocomplete': 'given-name'
        })
    )
    middle_name = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Middle name (optional)',
            'class': 'form-control',
            'autocomplete': 'additional-name'
        })
    )
    last_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name',
            'class': 'form-control',
            'autocomplete': 'family-name'
        })
    )
    id_number = forms.CharField(
        required=True,
        label='ID Number',
        widget=forms.TextInput(attrs={
            'placeholder': 'Student ID Number',
            'class': 'form-control'
        })
    )
    
    # Password fields
    password1 = forms.CharField(
        label='Password',
        help_text='Your password must contain at least 8 characters.',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    
    # Grade level and strand fields
    grade_level = forms.ChoiceField(
        required=True,
        choices=[
            ('', 'Select Grade Level'),
            ('7', 'Grade 7'),
            ('8', 'Grade 8'),
            ('9', 'Grade 9'),
            ('10', 'Grade 10'),
            ('11', 'Grade 11'),
            ('12', 'Grade 12')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_grade_level'
        })
    )
    
    strand = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Strand (SHS only)'),
            ('STEM', 'STEM'),
            ('ABM', 'ABM'),
            ('HUMSS', 'HUMSS'),
            ('GAS', 'GAS'),
            ('TVL', 'TVL')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_strand',
            'disabled': 'disabled'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class AdminCreateStudentForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    grade_level = forms.CharField(required=False)
    strand = forms.ChoiceField(required=False, choices=[
        ('', 'Select Strand'),
        ('STEM', 'STEM'),
        ('HUMSS', 'HUMSS'),
        ('GAS', 'GAS'),
        ('TVL', 'TVL'),
        ('ABM', 'ABM')
    ])
    id_number = forms.CharField(required=False)
    profile_image = forms.ImageField(required=False)


class PartyForm(forms.ModelForm):
    # New fields for adding candidates
    new_president = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2',
            'placeholder': 'Enter President Name'
        })
    )
    president_photo = forms.ImageField(required=False)
    
    new_vice_president = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2',
            'placeholder': 'Enter Vice President Name'
        })
    )
    vice_president_photo = forms.ImageField(required=False)
    
    new_secretary = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-2',
            'placeholder': 'Enter Secretary Name'
        })
    )
    secretary_photo = forms.ImageField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get or create positions
        self.president_position, _ = Position.objects.get_or_create(name='President')
        self.vice_president_position, _ = Position.objects.get_or_create(name='Vice President')
        self.secretary_position, _ = Position.objects.get_or_create(name='Secretary')
        
        # Filter candidates by position
        self.fields['president'].queryset = Candidate.objects.filter(position=self.president_position)
        self.fields['vice_president'].queryset = Candidate.objects.filter(position=self.vice_president_position)
        self.fields['secretary'].queryset = Candidate.objects.filter(position=self.secretary_position)
        
        # Make fields not required
        self.fields['president'].required = False
        self.fields['vice_president'].required = False
        self.fields['secretary'].required = False
        self.fields['team_name'].required = False
        
        # Set initial values for new candidate fields if editing
        if self.instance and self.instance.pk:
            if self.instance.president:
                self.fields['new_president'].initial = self.instance.president.name
            if self.instance.vice_president:
                self.fields['new_vice_president'].initial = self.instance.vice_president.name
            if self.instance.secretary:
                self.fields['new_secretary'].initial = self.instance.secretary.name

    class Meta:
        model = Party
        fields = ['name', 'team_name', 'president', 'vice_president', 'secretary']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Party name',
                'required': True
            }),
            'team_name': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Team name (e.g., Team Galing, Team Sigla)'
            }),
            'president': forms.Select(attrs={
                'class': 'form-select mb-3',
                'placeholder': 'Or select existing President'
            }),
            'vice_president': forms.Select(attrs={
                'class': 'form-select mb-3',
                'placeholder': 'Or select existing Vice President'
            }),
            'secretary': forms.Select(attrs={
                'class': 'form-select mb-3',
                'placeholder': 'Or select existing Secretary'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Party.objects.filter(name__iexact=name).exists():
            if self.instance and self.instance.pk:
                # If editing existing party and name hasn't changed, it's okay
                if self.instance.name.lower() == name.lower():
                    return name
            raise forms.ValidationError('A party with this name already exists.')
        return name
        
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if either new candidate or existing candidate is provided for each position
        for position in ['president', 'vice_president', 'secretary']:
            new_name = cleaned_data.get(f'new_{position}')
            existing = cleaned_data.get(position)
            
            if not new_name and not existing:
                self.add_error(position, f'Either select an existing {position} or enter a new one.')
                self.add_error(f'new_{position}', '')
                
            if new_name and existing:
                self.add_error(position, 'Please provide either an existing candidate or a new one, not both.')
                self.add_error(f'new_{position}', '')
        
        return cleaned_data
        
    def save(self, commit=True):
        party = super().save(commit=False)
        
        # Create or update candidates if new names are provided
        for position in ['president', 'vice_president', 'secretary']:
            new_name = self.cleaned_data.get(f'new_{position}')
            photo = self.cleaned_data.get(f'{position}_photo')
            position_obj = getattr(self, f'{position}_position')
            
            # Get the current candidate for this position if it exists
            current_candidate = getattr(party, position, None)
            
            if new_name:
                if current_candidate and current_candidate.name == new_name and not photo:
                    # If the name hasn't changed and no new photo, keep the existing candidate
                    pass
                else:
                    # Create new candidate or update existing
                    if current_candidate and current_candidate.name != new_name:
                        # If changing the candidate, create a new one
                        candidate = Candidate.objects.create(
                            name=new_name,
                            position=position_obj,
                            photo=photo or current_candidate.photo
                        )
                    else:
                        # Update existing candidate
                        if current_candidate:
                            current_candidate.name = new_name
                            if photo:  # Only update photo if a new one is provided
                                current_candidate.photo = photo
                            current_candidate.save()
                            candidate = current_candidate
                        else:
                            # Create new candidate
                            candidate = Candidate.objects.create(
                                name=new_name,
                                position=position_obj,
                                photo=photo
                            )
                    setattr(party, position, candidate)
            else:
                # If no new name is provided and there's an existing candidate, remove it
                if current_candidate:
                    setattr(party, position, None)
        
        if commit:
            party.save()
            self.save_m2m()
            
        return party


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g. President, Vice President, etc.'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Position.objects.filter(name__iexact=name).exists():
            if self.instance and self.instance.pk:
                # If editing existing position and name hasn't changed, it's okay
                if self.instance.name.lower() == name.lower():
                    return name
            raise forms.ValidationError('A position with this name already exists.')
        return name


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'position', 'party', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of the candidate'
            }),
            'position': forms.Select(attrs={
                'class': 'form-select',
            }),
            'party': forms.Select(attrs={
                'class': 'form-select',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make position and name required
        self.fields['name'].required = True
        self.fields['position'].required = True
        self.fields['party'].required = False
        self.fields['photo'].required = False


