from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # Страница сообщества
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    # Просмотр поста
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Создание поста
    path('create/', views.post_create, name='post_create'),
    # Редактирование поста
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Комментирование поста
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
