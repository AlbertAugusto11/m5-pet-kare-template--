from django.urls import path
from pets.views import PetDetailView, PetView

urlpatterns = [
    path('pets/', PetView.as_view()),
    path('pets/<int:pet_id>', PetDetailView.as_view()),
]
