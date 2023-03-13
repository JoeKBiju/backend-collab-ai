from django.urls import path
from .views import get_sentiment

urlpatterns = [
    path('', get_sentiment)
]