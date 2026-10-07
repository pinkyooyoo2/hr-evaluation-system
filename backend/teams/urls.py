from django.urls import path

from teams.views import team_detail, team_list_create

urlpatterns = [
    path('teams/', team_list_create, name='team-list-create'),
    path('teams/<int:pk>/', team_detail, name='team-detail'),
]
