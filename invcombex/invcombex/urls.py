# invcombex/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('invcg/', include('invcombex.urls')),
    path('invcg/', include('invcg.urls')),  # Esto conecta /invcg/ a las URLs de la app
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)