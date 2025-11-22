from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Voting app URLs with namespace
    path('', include('voting.urls')),
    
    # Add other app URLs here if needed
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization (commented out)
# admin.site.site_header = 'Voting System Admin'
# admin.site.site_title = 'Voting System Administration'
# admin.site.index_title = 'Database Administration'
