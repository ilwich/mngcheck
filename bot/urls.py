from django.urls import path
from . import views


app_name = 'bot'
urlpatterns = [
    path('hook/', views.talkin_to_me_bruh),
]