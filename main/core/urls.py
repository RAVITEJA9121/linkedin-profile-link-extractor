from django.urls import path
from .views import LinkedInView

urlpatterns = [
    path('',LinkedInView.as_view()),
]