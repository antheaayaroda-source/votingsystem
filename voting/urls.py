from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'voting'

urlpatterns = [
    # Root redirects to voter login page
    path('', RedirectView.as_view(url='/voter/login/', permanent=False)),

    # Backward compatibility: /login/ redirects to voter login
    path('login/', RedirectView.as_view(url='/voter/login/', permanent=False)),

    # Voter authentication
    path('voter/login/', views.student_auth, name='voter_login'),
    path('voter/signin/', views.student_auth, name='voter_signin'),  # alias
    path('voter/register/', views.register, name='register'),

    # Voter logout
    path('logout/', views.voter_logout, name='voter_logout'),
    
    # Welcome page
    path('welcome/', views.welcome_page, name='welcome'),

    # Admin authentication
    path('admin/login/', views.admin_login, name='admin_login'),
    # Use a dashboard-scoped logout path to avoid colliding with Django's admin/ URLs
    path('dashboard/logout/', views.admin_logout, name='admin_logout'),

    # Admin dashboard and management (using 'dashboard' instead of 'admin/dashboard')
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/stats/', views.admin_dashboard_stats, name='admin_dashboard_stats'),
    
    # Admin management
    path('dashboard/candidates/', views.admin_candidates, name='admin_candidates'),
    path('dashboard/candidates/add/', views.admin_add_candidate, name='admin_add_candidate'),
    path('dashboard/candidates/<int:pk>/edit/', views.admin_edit_candidate, name='admin_edit_candidate'),
    path('dashboard/candidates/<int:candidate_id>/delete/', views.admin_delete_candidate, name='admin_delete_candidate'),

    path('dashboard/parties/', views.admin_parties, name='admin_parties'),
    path('dashboard/parties/add/', views.admin_add_party, name='admin_add_party'),
    path('dashboard/parties/<int:party_id>/delete/', views.admin_delete_party, name='admin_delete_party'),
    path('dashboard/parties/<int:party_id>/edit/', views.admin_edit_party, name='admin_edit_party'),
    path('dashboard/voters/add/', views.admin_add_voter, name='admin_add_voter'),
    path('dashboard/voters/', views.admin_voters, name='admin_voters'),
    path('dashboard/export-results/', views.admin_export_results, name='admin_export_results'),
    path('dashboard/toggle-voting/', views.toggle_voting, name='toggle_voting'),
    path('dashboard/rules/', views.admin_rules, name='admin_rules'),
    path('dashboard/teams/', views.admin_teams, name='admin_teams'),
    path('dashboard/teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('dashboard/positions/', views.admin_positions, name='admin_positions'),
    path('dashboard/votes/', views.admin_votes, name='admin_votes'),

    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='voting/password_reset.html',
             email_template_name='voting/password_reset_email.html',
             subject_template_name='voting/password_reset_subject.txt',
             success_url='/voter/signin/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='voting/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='voting/password_reset_confirm.html',
             success_url='/voter/signin/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='voting/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Voting URLs
    path('vote/', views.vote_page, name='vote_page'),
    path('vote/success/', views.vote_success, name='vote_success'),
    path('submit-vote/', views.submit_votes, name='submit_vote'),

    # Voter profile/info
    path('voter/info/', views.voter_info, name='voter_info'),
    
    # About page
    path('about/', views.about_page, name='about'),
]
