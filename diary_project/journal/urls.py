"""
URL configuration for diary_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views
from .views import profile_view
urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_entry, name='add_entry'),
    path('entry/<int:entry_id>/', views.entry_detail, name='entry_detail'),  # 👈 New
    path('register/', views.register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('add-reminder/', views.add_reminder, name='add_reminder'),

path('reminder/delete/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),



]

