from django.shortcuts import render, redirect, get_object_or_404
from django.db import models, transaction
from django.db.models import Sum, Q, Count
from django.db.models.functions import Coalesce
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
import logging

# Module logger for debugging
logger = logging.getLogger(__name__)

from .forms import LoginForm, RegistrationForm, PartyForm, CandidateForm
from .models import Voter, Position, Candidate, Vote, Party

# ----------------------
# Admin Decorator
# ----------------------
def admin_required(view_func):
    """Decorator for admin-only views."""
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='voting:admin_login',
        redirect_field_name=None
    )
    return actual_decorator(view_func)

# ----------------------
# Admin Views
# ----------------------
def admin_login(request):
    """Admin login page."""
    # If user is already authenticated and is staff, redirect to admin dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('voting:admin_dashboard')
        
    # Handle login form submission
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('voting:admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # For GET requests, show the login form
    return render(request, 'voting/admin/login.html')


def admin_logout(request):
    """Logout admin user and redirect to voter login page."""
    logger.info("admin_logout called; path=%s method=%s user=%s", request.path, request.method, getattr(request.user, 'username', None))
    # Also print to stdout so runserver console definitely shows the event
    print(f"DEBUG: admin_logout called; path={request.path} method={request.method} user={getattr(request.user,'username',None)}")
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have successfully logged out.')
    # Redirect explicitly to the voter login path to avoid hitting Django's default
    # auth/login or admin login pages accidentally.
    logger.info("admin_logout redirecting to /voter/login/")
    print("DEBUG: admin_logout redirecting to /voter/login/")
    return redirect('/voter/login/')  # explicit path to voter login


@admin_required
def admin_dashboard(request):
    """Admin dashboard showing summary statistics and system overview."""
    from django.db.models import Count, Sum
    from django.db.models.functions import Coalesce
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    from datetime import timedelta
    
    # Basic counts
    total_voters = Voter.objects.count()
    total_votes = Vote.objects.count()
    total_candidates = Candidate.objects.count()
    total_parties = Party.objects.count()
    
    # Active users (users with active sessions in the last 30 minutes)
    thirty_min_ago = timezone.now() - timedelta(minutes=30)
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    active_users_count = len(set(session.get_decoded().get('_auth_user_id') for session in active_sessions))
    
    # Voting status (check if voting is enabled)
    voting_enabled = not getattr(settings, 'VOTING_PAUSED', False)
    
    # Recent activities (last 10)
    recent_activities = []
    
    # Add recent votes as activities
    recent_votes = Vote.objects.select_related('voter__user', 'candidate')\
                             .order_by('-created_at')[:5]
    for vote in recent_votes:
        recent_activities.append({
            'action': f'Vote cast for {vote.candidate.name}',
            'timestamp': vote.created_at,
            'details': f'Voter: {vote.voter.user.username}'
        })
    
    # Add recent voter registrations
    recent_voters = Voter.objects.select_related('user')\
                               .order_by('-id')[:5]
    for voter in recent_voters:
        recent_activities.append({
            'action': 'New voter registered',
            'timestamp': voter.user.date_joined,
            'details': f'ID: {voter.id_number}'
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]  # Get only the 10 most recent
    
    # Position statistics
    positions = Position.objects.annotate(
        num_candidates=Count('candidate'),
        num_votes=Count('candidate__vote')
    )
    
    # Party statistics
    parties = Party.objects.annotate(
        num_candidates=Count('candidate'),
        num_votes=Count('candidate__votes')
    ).order_by('-num_votes')
    
    context = {
        # Basic counts
        'total_voters': total_voters,
        'total_votes': total_votes,
        'total_candidates': total_candidates,
        'total_parties': total_parties,
        
        # System status
        'voting_enabled': voting_enabled,
        'active_users_count': active_users_count,
        
        # Recent activities
        'recent_activities': recent_activities,
        'recent_votes': recent_votes[:5],  # For the recent votes section
        
        # Statistics
        'positions': positions,
        'parties': parties,
        
        # Current date/time (will be used in template with template tags)
    }
    
    return render(request, 'voting/admin/dashboard.html', context)


@admin_required
def admin_dashboard_stats(request):
    """Return JSON stats for the admin dashboard (used by AJAX)."""
    from django.http import JsonResponse
    from django.utils import timezone
    from django.contrib.sessions.models import Session

    total_voters = Voter.objects.count()
    total_votes = Vote.objects.count()
    total_candidates = Candidate.objects.count()
    total_parties = Party.objects.count()

    # Active users (sessions that haven't expired)
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    active_users_count = len(set(session.get_decoded().get('_auth_user_id') for session in active_sessions))

    data = {
        'total_voters': total_voters,
        'total_votes': total_votes,
        'total_candidates': total_candidates,
        'total_parties': total_parties,
        'active_users_count': active_users_count,
    }

    return JsonResponse(data)


@admin_required
def admin_candidates(request):
    candidates = Candidate.objects.select_related('position', 'party').all()
    positions = Position.objects.all()
    parties = Party.objects.all()
    return render(request, 'voting/admin/candidates.html', {
        'candidates': candidates,
        'positions': positions,
        'parties': parties,
    })


@admin_required
def admin_add_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'Candidate "{form.cleaned_data.get("name")}" added.')
            return redirect('voting:admin_candidates')
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
    else:
        form = CandidateForm()

    return render(request, 'voting/admin/candidate_form.html', {
        'form': form,
        'form_action': 'Add',
    })


@admin_required
def admin_edit_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, f'Candidate "{form.cleaned_data.get("name")}" updated.')
            return redirect('voting:admin_candidates')
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{field}: {err}")
    else:
        form = CandidateForm(instance=candidate)

    return render(request, 'voting/admin/candidate_form.html', {
        'form': form,
        'form_action': 'Update',
        'form_title': f'Edit Candidate: {candidate.name}',
    })


@admin_required
def admin_edit_party(request, party_id):
    """Edit an existing political party."""
    from django.shortcuts import get_object_or_404, redirect
    from .models import Party
    from .forms import PartyForm
    
    # Try to get the party; if it's already deleted, show a friendly message
    try:
        party = Party.objects.get(id=party_id)
    except Party.DoesNotExist:
        messages.error(request, 'Party not found or already deleted.')
        return redirect('voting:admin_parties')
    
    if request.method == 'POST':
        form = PartyForm(request.POST, request.FILES, instance=party)
        if form.is_valid():
            form.save()
            messages.success(request, f'Successfully updated {party.name}')
            return redirect('voting:admin_parties')
    else:
        form = PartyForm(instance=party)
    
    return render(request, 'voting/admin/party_form.html', {
        'title': f'Edit {party.name}',
        'form': form,
        'party': party
    })


@admin_required
def admin_parties(request):
    """Admin view for managing political parties with their candidates."""
    # Get all parties with their candidates
    parties = Party.objects.prefetch_related(
        'president',
        'vice_president',
        'secretary'
    ).order_by('name')
    
    # Do NOT auto-create default teams here. Only include them if they exist.
    team_galing = Party.objects.filter(team_name__iexact='TEAM GALING').first()
    team_sigla = Party.objects.filter(team_name__iexact='TEAM SIGLA').first()

    # Ensure we include existing default teams, but don't create them automatically
    all_parties = list(parties)
    if team_galing and team_galing not in all_parties:
        all_parties.append(team_galing)
    if team_sigla and team_sigla not in all_parties:
        all_parties.append(team_sigla)
    
    return render(request, 'voting/admin/parties.html', {
        'title': 'Political Parties',
        'parties': all_parties
    })


@admin_required
def admin_delete_party(request, party_id):
    """Delete a political party and its associated candidates."""
    from django.shortcuts import get_object_or_404, redirect
    from django.views.decorators.http import require_POST
    from .models import Party, Candidate
    
    party = get_object_or_404(Party, id=party_id)
    
    if request.method == 'POST':
        try:
            # First, delete all candidates associated with this party
            Candidate.objects.filter(party=party).delete()
            
            # Then delete the party
            party_name = party.name
            party.delete()
            
            messages.success(request, f'Successfully deleted party and its candidates: {party_name}')
            return redirect('voting:admin_parties')
            
        except Exception as e:
            messages.error(request, f'Error deleting party: {str(e)}')
            return redirect('voting:admin_parties')
    
    # If not POST, redirect to parties list
    messages.error(request, 'Invalid request method')
    return redirect('voting:admin_parties')


@admin_required
def admin_add_voter(request):
    """Admin view to add a new voter."""
    if request.method == 'POST':
        username = request.POST.get('username')
        id_number = request.POST.get('id_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([username, id_number, first_name, last_name, email, password]):
            messages.error(request, 'All fields are required.')
            return redirect('voting:admin_add_voter')

        try:
            # Check if username or ID number already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect('voting:admin_add_voter')

            if Voter.objects.filter(id_number=id_number).exists():
                messages.error(request, 'Voter with this ID number already exists.')
                return redirect('voting:admin_add_voter')

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Create voter profile
            Voter.objects.create(
                user=user,
                id_number=id_number,
                has_voted=False
            )

            messages.success(request, f'Voter {username} added successfully.')
            return redirect('voting:admin_voters')

        except Exception as e:
            messages.error(request, f'Error adding voter: {str(e)}')

    return render(request, 'voting/admin/voter_form.html', {
        'title': 'Add New Voter',
        'form_action': 'Add'
    })


@admin_required
def admin_export_results(request):
    """Export voting results to CSV."""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="election_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'},
    )
    
    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow(['Position', 'Candidate', 'Party', 'Votes Received'])
    
    # Get all positions
    positions = Position.objects.all().order_by('priority')
    
    # Write data for each position
    for position in positions:
        candidates = Candidate.objects.filter(position=position).order_by('-vote_count')
        
        if candidates.exists():
            for candidate in candidates:
                writer.writerow([
                    position.name,
                    f"{candidate.user.last_name}, {candidate.user.first_name}",
                    candidate.party.name if candidate.party else 'Independent',
                    candidate.vote_count
                ])
        else:
            writer.writerow([position.name, 'No candidates', '', 0])
        
        # Add an empty row between positions for better readability
        writer.writerow([])
    
    # Add summary statistics
    total_voters = Voter.objects.count()
    voted_count = Voter.objects.filter(has_voted=True).count()
    abstain_count = total_voters - voted_count
    
    writer.writerow(['Voting Statistics', '', '', ''])
    writer.writerow(['Total Registered Voters', total_voters, '', ''])
    writer.writerow(['Total Votes Cast', voted_count, '', ''])
    writer.writerow(['Voter Turnout', f'{(voted_count/total_voters*100):.2f}%', '', ''] if total_voters > 0 else ['Voter Turnout', 'N/A', '', ''])
    writer.writerow(['Abstentions', abstain_count, '', ''])
    
    return response


@admin_required
def admin_delete_candidate(request, candidate_id):
    """Delete a candidate."""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import Candidate
    
    if request.method == 'POST':
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate_name = str(candidate)
        try:
            candidate.delete()

            # If AJAX request, return JSON so frontend can handle without redirect
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_ACCEPT', '').find('application/json') != -1:
                from django.http import JsonResponse
                return JsonResponse({'success': True, 'message': f'Successfully deleted candidate: {candidate_name}'})

            messages.success(request, f'Successfully deleted candidate: {candidate_name}')
        except Exception as e:
            # If AJAX request, return JSON error
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_ACCEPT', '').find('application/json') != -1:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': str(e)}, status=400)

            messages.error(request, f'Error deleting candidate: {str(e)}')

    return redirect('voting:admin_candidates')


@admin_required
def toggle_voting(request):
    """Toggle voting status between enabled and disabled."""
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    from django.conf import settings
    from django.core.cache import cache
    
    if request.method == 'POST':
        try:
            # Toggle the voting status
            current_status = not settings.VOTING_ENABLED
            
            # Update the setting (you might want to store this in the database or cache)
            # For this example, we'll use Django's cache
            cache.set('voting_enabled', current_status, timeout=None)
            
            # If you're using a custom settings module, you might want to update it like this:
            # from django.conf import settings
            # settings.VOTING_ENABLED = current_status
            
            return JsonResponse({
                'status': 'success',
                'enabled': current_status,
                'message': 'Voting has been ' + ('enabled' if current_status else 'disabled')
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


@admin_required
def admin_add_party(request):
    """Admin view to add a new political party with team assignments."""
    if request.method == 'POST':
        form = PartyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the party with form data
                    party = form.save()
                    
                    # Get or create positions
                    president_pos, _ = Position.objects.get_or_create(name='President')
                    vice_president_pos, _ = Position.objects.get_or_create(name='Vice President')
                    secretary_pos, _ = Position.objects.get_or_create(name='Secretary')
                    
                    # Handle new candidates if provided
                    for position_field, position_obj in [
                        ('president', president_pos),
                        ('vice_president', vice_president_pos),
                        ('secretary', secretary_pos)
                    ]:
                        new_name = form.cleaned_data.get(f'new_{position_field}')
                        photo = form.cleaned_data.get(f'{position_field}_photo')
                        
                        if new_name:
                            # Create new candidate
                            candidate = Candidate.objects.create(
                                name=new_name,
                                position=position_obj,
                                photo=photo,
                                party=party
                            )
                            # Assign the new candidate to the party
                            setattr(party, position_field, candidate)
                    
                    party.save()
                    messages.success(request, f'Party "{party.name}" and candidates added successfully.')
                    return redirect('voting:admin_parties')
                    
            except Exception as e:
                messages.error(request, f'Error adding party: {str(e)}')
        else:
            # If form is not valid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PartyForm()
    
    return render(request, 'voting/admin/party_form.html', {
        'title': 'Add New Political Party',
        'form': form,
        'form_action': 'Add'
    })


@admin_required
def admin_edit_party(request, party_id):
    """Edit an existing political party with team assignments."""
    party = get_object_or_404(Party, id=party_id)
    
    if request.method == 'POST':
        form = PartyForm(request.POST, request.FILES, instance=party)
        if form.is_valid():
            try:
                # Save the party with form data
                updated_party = form.save(commit=False)
                updated_party.save()
                
                # Save many-to-many relationships if any
                form.save_m2m()
                
                messages.success(request, f'Party "{updated_party.name}" updated successfully.')
                return redirect('voting:admin_parties')
            except Exception as e:
                messages.error(request, f'Error updating party: {str(e)}')
        else:
            # If form is not valid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PartyForm(instance=party)
    
    return render(request, 'voting/admin/party_form.html', {
        'title': f'Edit {party.name}',
        'form': form,
        'form_action': 'Update',
        'party': party
    })


@admin_required
def admin_positions(request):
    """Admin view to manage voting positions."""
    positions = Position.objects.all().order_by('name')
    return render(request, 'voting/admin/positions.html', {
        'positions': positions,
        'title': 'Manage Positions'
    })


@admin_required
def admin_voters(request):
    # Exclude admin and superuser accounts from the voters list
    voters = Voter.objects.select_related('user')\
                         .filter(user__is_staff=False, user__is_superuser=False)\
                         .order_by('-user__date_joined')
    
    grade_level = request.GET.get('grade_level')
    strand = request.GET.get('strand')
    has_voted = request.GET.get('has_voted')

    if grade_level:
        voters = voters.filter(grade_level=grade_level)
    if strand:
        voters = voters.filter(strand=strand)
    if has_voted is not None:
        voters = voters.filter(has_voted=bool(has_voted))

    # Convert to list and attach sequential numbers for display
    voters_list = list(voters)
    for idx, v in enumerate(voters_list, start=1):
        setattr(v, 'seq', idx)

    context = {
        'voters': voters_list,
        'grade_levels': Voter.objects.filter(user__is_staff=False, user__is_superuser=False)
                                   .values_list('grade_level', flat=True).distinct(),
        'strands': Voter.objects.filter(user__is_staff=False, user__is_superuser=False)
                              .exclude(strand='').values_list('strand', flat=True).distinct(),
    }
    return render(request, 'voting/admin/voters.html', context)


@admin_required
def admin_votes(request):
    # Get all votes with related data
    votes = Vote.objects.select_related('voter', 'candidate__user', 'candidate__position').all()
    
    # Group votes by position for the template
    votes_by_position = {}
    for position in Position.objects.all():
        votes_by_position[position] = votes.filter(candidate__position=position)
    
    context = {
        'title': 'Vote Records',
        'votes_by_position': votes_by_position,
        'total_votes': votes.count(),
    }
    return render(request, 'voting/admin/votes.html', context)

@admin_required
def admin_rules(request):
    """Admin view for managing voting rules."""
    context = {
        'title': 'Voting Rules',
    }
    return render(request, 'voting/admin/rules.html', context)

@admin_required
def admin_teams(request):
    """Admin view for managing teams and their candidates."""
    # Get all parties with their candidates
    parties = Party.objects.all().prefetch_related(
        'president',
        'vice_president',
        'secretary'
    )
    
    # Do NOT auto-create teams here; only fetch existing ones
    team_galing = Party.objects.filter(team_name__iexact='TEAM GALING').first()
    team_sigla = Party.objects.filter(team_name__iexact='TEAM SIGLA').first()
    
    # Get all candidates for the dropdowns
    positions = Position.objects.all()

    # Build a safe list of existing teams (exclude None)
    teams = []
    if team_galing:
        teams.append(team_galing)
    if team_sigla:
        teams.append(team_sigla)

    context = {
        'title': 'Teams and Candidates',
        'parties': teams,
        'positions': positions,
    }
    
    return render(request, 'voting/admin/teams_new.html', context)

@admin_required
def team_detail(request, team_id):
    """View for displaying team details and candidates."""
    team = get_object_or_404(
        Party.objects.select_related('president', 'vice_president', 'secretary'),
        pk=team_id
    )
    
    context = {
        'title': f'{team.team_name} - Team Details',
        'team': team,
    }
    return render(request, 'voting/admin/team_detail.html', context)

# ----------------------
# Voter Views
# ----------------------
# separate registration view
def register(request):
    if request.user.is_authenticated:
        return redirect('voting:vote_page')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            Voter.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                middle_name=form.cleaned_data.get('middle_name', ''),
                last_name=form.cleaned_data['last_name'],
                id_number=form.cleaned_data['id_number'],
                grade_level=request.POST.get('grade_level', ''),
                strand=request.POST.get('strand', '') if request.POST.get('grade_level') in ['11','12'] else ''
            )

            login(request, user)
            messages.success(request, "Registration successful! You can now cast your vote.")
            return redirect('voting:vote_page')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'voting/register.html', {'form': form})

# student login view (login only)
def student_auth(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('voting:admin_dashboard')
        return redirect('voting:vote_page')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me') == 'on'

        if not username or not password:
            messages.error(request, 'Please enter your Username/Student ID and Password.', extra_tags='error')
            return render(request, 'voting/login.html')

        # Try to authenticate with the provided credentials
        user = authenticate(request, username=username, password=password)
        
        # If authentication fails, try with student_id if username is numeric
        if user is None and username.isdigit():
            try:
                # Try to find a user with matching student ID
                voter = Voter.objects.get(id_number=username)
                user = authenticate(request, username=voter.user.username, password=password)
            except Voter.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)

            # Check if user is staff/admin
            if user.is_staff:
                # Redirect to the admin dashboard using URL name
                return redirect('voting:admin_dashboard')  # This now points to /dashboard/

            # Handle regular voter login
            try:
                voter = Voter.objects.get(user=user)
                if voter.has_voted:
                    messages.info(request, 'You have already voted.')
                    return redirect('voting:vote_success')
            except Voter.DoesNotExist:
                # If no voter record exists, create one
                Voter.objects.create(user=user, id_number=username if username.isdigit() else '')

            messages.success(request, 'Successfully logged in! You can now vote.')
            next_url = request.GET.get('next', 'voting:vote_page')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid Username/Student ID or password.', extra_tags='error')
            return render(request, 'voting/login.html')

    # GET request
    return render(request, 'voting/login.html')

def voter_login(request):
    """Redirect to new login page."""
    return redirect('voting:voter_signin')


def voter_logout(request):
    logger.info("voter_logout called; path=%s method=%s user=%s", request.path, request.method, getattr(request.user, 'username', None))
    print(f"DEBUG: voter_logout called; path={request.path} method={request.method} user={getattr(request.user,'username',None)}")
    if request.method in ['GET', 'POST']:
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'You have successfully logged out.')
        else:
            messages.info(request, 'Wala kang naka-login na account.')
    logger.info("voter_logout redirecting to /voter/login/")
    print("DEBUG: voter_logout redirecting to /voter/login/")
    # Use explicit path to ensure we land on the voter login page, not Django auth.
    return redirect('/voter/login/')


@login_required
def voter_info(request):
    voter = get_object_or_404(Voter, user=request.user)
    missing = [f for f in ('first_name', 'last_name', 'grade_level') if not getattr(voter, f)]
    if missing:
        messages.warning(request, "Please complete your information before voting.")
        return redirect('voting:register')
    return redirect('voting:vote_page')


# ----------------------
# Welcome Page View
# ----------------------
def welcome_page(request):
    """Display the welcome page with candidates and voting information."""
    # Get all active candidates with their positions and parties
    candidates = Candidate.objects.filter(is_active=True).select_related('position', 'party')
    positions = Position.objects.all().order_by('order')
    
    # Organize candidates by position and party
    candidates_by_position = {}
    for position in positions:
        candidates_by_position[position] = {
            'TEAM GALING': candidates.filter(position=position, party__name='TEAM GALING'),
            'TEAM SIGLA': candidates.filter(position=position, party__name='TEAM SIGLA')
        }
    
    # Team rules
    team_galing_rules = [
        "EXCELLENCE FIRST - Strive for academic excellence and leadership in all school activities.",
        "INTEGRITY AND HONESTY - Be truthful in all your actions and decisions.",
        "RESPECT AND FAIRNESS - Treat everyone with respect and fairness.",
        "LEAD BY EXAMPLE - Show good behavior and set a positive example for others.",
        "VISION FOR ALL - Focus on initiatives that benefit the entire student body."
    ]
    
    team_sigla_rules = [
        "BE A ROLE MODEL - Show positivity, discipline, and teamwork at all times.",
        "CAMPAIGN WITH ENERGY AND RESPECT - Promote team goals cheerfully and respectfully.",
        "PROMOTE SCHOOL SPIRIT - Encourage participation in school activities.",
        "CREATIVE AND HONEST CAMPAIGN - Use creative materials that reflect true mission.",
        "SERVE BEFORE YOU LEAD - Demonstrate leadership through service to others."
    ]
    
    context = {
        'candidates_by_position': candidates_by_position,
        'team_galing_rules': team_galing_rules,
        'team_sigla_rules': team_sigla_rules,
        'is_authenticated': request.user.is_authenticated,
        'is_admin': request.user.is_authenticated and request.user.is_staff
    }
    
    return render(request, 'voting/welcome.html', context)

# ----------------------
# Voting Views
# ----------------------
@login_required
def vote_page(request):
    voter = get_object_or_404(Voter, user=request.user)
    if voter.has_voted:
        messages.info(request, "You have already voted.")
        return redirect('voting:vote_success')

    # Get all positions with their candidates
    all_positions = Position.objects.prefetch_related('candidate_set').all()
    
    # Clean position names and handle duplicates
    def normalize_position_name(name):
        if not name:
            return ''
        # Convert to lowercase and remove any extra spaces
        return ' '.join(str(name).strip().lower().split())
    
    # Group positions by their normalized name
    position_map = {}
    for pos in all_positions:
        norm_name = normalize_position_name(pos.name)
        if norm_name not in position_map:
            position_map[norm_name] = []
        position_map[norm_name].append(pos)
    
    # Clean position names for display and add position type
    def get_display_info(name):
        name = str(name).strip()
        norm_name = normalize_position_name(name)
        
        # Map position types to their display names
        position_types = {
            'president': 'PRESIDENT',
            'vice president': 'VICE PRESIDENT',
            'v-president': 'VICE PRESIDENT',
            'secretary': 'SECRETARY'
        }
        
        # Check if this is a main position
        for pos_name, display_name in position_types.items():
            if pos_name in norm_name:
                return {
                    'display_name': '',  # No title for main positions
                    'position_type': display_name
                }
        
        # For other positions, return the name as is
        return {
            'display_name': name,
            'position_type': ''
        }
    
    # Create a list of positions with their candidates
    positions = []
    seen_names = set()
    
    # First add the main positions in the correct order
    main_positions = [
        ('president', 'PRESIDENT'),
        ('vice president', 'VICE PRESIDENT'),
        ('v-president', 'VICE PRESIDENT'),  # Handle both formats
        ('secretary', 'SECRETARY')
    ]
    
    # Track which main positions we've already added
    added_positions = set()
    
    # First, handle the main positions
    for norm_name, display_name in main_positions:
        if norm_name in position_map and norm_name not in seen_names:
            # Get the first position with this name that has candidates
            for pos in position_map[norm_name]:
                if pos.candidate_set.exists():
                    # Only add if we haven't added this position type yet
                    if display_name not in added_positions:
                        pos.display_name = ''
                        pos.position_type = display_name
                        positions.append(pos)
                        added_positions.add(display_name)
                    seen_names.add(norm_name)
                    break
    
    # Add other positions that aren't in the main positions list
    for norm_name, pos_list in position_map.items():
        if norm_name not in seen_names:
            for pos in pos_list:
                if pos.candidate_set.exists():
                    display_info = get_display_info(pos.name)
                    pos.display_name = display_info['display_name']
                    pos.position_type = display_info['position_type']
                    positions.append(pos)
                    break
    
    # Custom sort to maintain consistent order
    def position_order(pos):
        name = pos.name.lower()
        if 'president' in name and 'vice' not in name:
            return 0
        elif 'vice president' in name or 'v-president' in name:
            return 1
        elif 'secretary' in name:
            return 2
        else:
            return 3  # Other positions come after
    
    positions = sorted(positions, key=position_order)
    parties = Party.objects.all()

    # Build a positions_view structure to support the template's left/right layout
    # left_party corresponds to TEAM SIGLA and right_party to TEAM GALING (if they exist)
    left_party = Party.objects.filter(team_name__iexact='TEAM SIGLA').first()
    right_party = Party.objects.filter(team_name__iexact='TEAM GALING').first()

    positions_view = []
    has_any_pairs = False
    for pos in positions:
        left_cand = None
        right_cand = None
        if left_party:
            left_cand = Candidate.objects.filter(position=pos, party=left_party).first()
        if right_party:
            right_cand = Candidate.objects.filter(position=pos, party=right_party).first()
        if left_cand or right_cand:
            has_any_pairs = True
        positions_view.append({
            'position': pos,
            'left': left_cand,
            'right': right_cand
        })

    if request.method == "POST":
        selections = {pos.id: request.POST.get(str(pos.id)) for pos in positions}
        missing_positions = [pos.name for pos in positions if not selections.get(pos.id)]
        if missing_positions:
            messages.error(request, "Please select a candidate for: " + ", ".join(missing_positions))
            return render(request, 'voting/vote.html', {'positions': positions, 'parties': parties})
        request.session['vote_selections'] = selections
        positions_with_candidates = {Position.objects.get(id=k).name: Candidate.objects.get(id=v) for k, v in selections.items()}
        return render(request, 'voting/vote_confirm.html', {'positions_with_candidates': positions_with_candidates, 'selections': selections})

    # compute sequential number and voted counts
    total_voters = Voter.objects.filter(user__is_staff=False, user__is_superuser=False).count()
    # sequence based on primary key ordering (1-based)
    voter_seq = Voter.objects.filter(user__is_staff=False, user__is_superuser=False, id__lte=voter.id).count()
    voted_count = Voter.objects.filter(has_voted=True).count()

    # Get all parties with rules
    all_parties = Party.objects.all()
    
    return render(request, 'voting/vote.html', {
        'positions': positions,
        'parties': parties,
        'voter_seq': voter_seq,
        'total_voters': total_voters,
        'voted_count': voted_count,
        'positions_view': positions_view,
        'has_any_pairs': has_any_pairs,
        'left_party': left_party,
        'right_party': right_party,
        'all_parties': all_parties,
    })


@login_required
def submit_votes(request):
    if request.method != 'POST':
        return redirect('voting:vote_page')

    voter = get_object_or_404(Voter, user=request.user)
    selections = request.POST.dict()
    selections.pop('csrfmiddlewaretoken', None)

    if not selections:
        messages.warning(request, "No votes submitted.")
        return redirect('voting:vote_page')

    try:
        with transaction.atomic():
            Vote.objects.filter(voter=voter).delete()
            for pos_id, cand_id in selections.items():
                candidate = get_object_or_404(Candidate, id=int(cand_id))
                Vote.objects.create(voter=voter, candidate=candidate)
            voter.has_voted = True
            voter.save()
    except Exception:
        messages.error(request, "Error saving votes.")
        return redirect('voting:vote_page')

    request.session.pop('vote_selections', None)
    messages.success(request, "Your votes have been recorded.")
    return redirect('voting:vote_success')


@login_required
def vote_success(request):
    voter = get_object_or_404(Voter, user=request.user)
    votes = Vote.objects.filter(voter=voter).select_related('candidate', 'candidate__position')
    if not votes.exists():
        messages.warning(request, "Please cast your vote first.")
        return redirect('voting:vote_page')

    votes_by_position = {vote.candidate.position.name: vote.candidate for vote in votes}
    # also include voter sequence and counts for the success page
    total_voters = Voter.objects.filter(user__is_staff=False, user__is_superuser=False).count()
    voter_seq = Voter.objects.filter(user__is_staff=False, user__is_superuser=False, id__lte=voter.id).count()
    voted_count = Voter.objects.filter(has_voted=True).count()

    return render(request, 'voting/vote_success.html', {
        'votes_by_position': votes_by_position,
        'voter_seq': voter_seq,
        'total_voters': total_voters,
        'voted_count': voted_count,
    })


def about_page(request):
    return render(request, 'voting/about.html')
