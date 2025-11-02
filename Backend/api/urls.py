from django.urls import path,include
from . import views 

urlpatterns = [
    path('profile/', views.get_profile, name='get_profile'),
]
