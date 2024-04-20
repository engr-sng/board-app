# app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', login_required(views.new), name='new'),
    path('create/', login_required(views.create), name='create'),
    path('<int:pk>/', login_required(views.show), name='show'),
    path('<int:pk>/edit/', login_required(views.edit), name='edit'),
    path('<int:pk>/update/', login_required(views.update), name='update'),
    path('<int:pk>/delete/', login_required(views.delete), name='delete'),
    path('<int:pk>/comment/', login_required(views.comment_create), name='comment_create'),
    path('<int:board_pk>/comment/<int:comment_pk>/delete/', login_required(views.comment_delete), name='comment_delete'),
    path('my_boards/', login_required(views.my_boards), name='my_boards'),
]