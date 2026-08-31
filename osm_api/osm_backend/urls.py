from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('api/admin/', admin.site.urls),

    # API
    path('api/web/', include('apps.web_app.urls')),
    path('api/osm/', include('apps.id_editor.urls')),
    path('api/', include('apps.osm_protocol.urls')),
    path('oauth2/', include('apps.oauth2_server.urls')),  
   path('api/map-layers/', include('apps.map_layers.api')), 

    # Docs
    path('api/swagger/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)