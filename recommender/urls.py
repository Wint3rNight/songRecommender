from django.urls import path
from .views import home_view, get_recommendation

urlpatterns = [
    path('', home_view, name='home'),
    path('api/recommend/', get_recommendation, name='get_recommendation'),
]