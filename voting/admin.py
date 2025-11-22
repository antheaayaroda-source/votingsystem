from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count
from .models import Candidate, Position, Voter, Vote, Party

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("name", "team_name", "get_president", "get_vice_president", "get_secretary")
    search_fields = ("name", "team_name")
    list_filter = ("team_name",)
    
    def get_president(self, obj):
        return obj.president.name if obj.president else "-"
    get_president.short_description = "President"
    
    def get_vice_president(self, obj):
        return obj.vice_president.name if obj.vice_president else "-"
    get_vice_president.short_description = "Vice President"
    
    def get_secretary(self, obj):
        return obj.secretary.name if obj.secretary else "-"
    get_secretary.short_description = "Secretary"


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "party", "vote_count")
    list_filter = ("position", "party")
    search_fields = ("name", "position__name", "party__name")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_votes=Count("vote"))

    def vote_count(self, obj):
        return getattr(obj, "_votes", 0)
    vote_count.short_description = "Votes"


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ("user_username", "user_email", "first_name", "middle_name", "last_name", "grade_level", "strand", "id_number", "has_voted")
    list_filter = ("has_voted", "grade_level", "strand")
    search_fields = ("user__username", "user__email", "first_name", "middle_name", "last_name", "id_number")
    readonly_fields = ()

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = "Username"

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "candidate", "created_at")
    list_filter = ("candidate__position", "candidate", "created_at")
    search_fields = ("voter__user__username", "candidate__name")
    date_hierarchy = "created_at"
    change_list_template = "admin/voting/vote/change_list.html"

    def changelist_view(self, request, extra_context=None):
        candidate_totals = (
            Vote.objects.values(
                "candidate__id",
                "candidate__name",
                "candidate__position__name",
            )
            .annotate(total=Count("id"))
            .order_by("-total", "candidate__name")
        )

        extra = {
            "candidate_totals": candidate_totals,
            "overall_votes": Vote.objects.count(),
        }
        if extra_context:
            extra.update(extra_context)
        return super().changelist_view(request, extra_context=extra)


# Ensure default User admin is replaced by our customized one
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )