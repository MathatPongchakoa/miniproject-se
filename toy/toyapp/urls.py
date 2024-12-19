from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', toy_list, name='toy_list'),
    path('<int:toy_id>/', toy_detail, name='toy_detail'),
    path('<int:toy_id>/favorite/', add_to_favorites, name='add_to_favorites'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('add-toy/', add_toy, name='add_toy'),
    path('add-category/', add_category, name='add_category'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)