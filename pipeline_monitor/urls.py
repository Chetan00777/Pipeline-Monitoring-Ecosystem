from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('',          include('dashboard.urls')),   # Main dashboard
    path('fog/',      include('fog_node.urls')),    # Fog node ingest endpoint
]
