from django.urls import path

from users.views import admin_user_detail, admin_user_list_create, login_view, logout_view, me_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('me/', me_view, name='me'),
    path('users/', admin_user_list_create, name='admin-user-list-create'),
    path('users/<int:pk>/', admin_user_detail, name='admin-user-detail'),
]
