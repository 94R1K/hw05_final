from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    # Главная страница
    path('', include('posts.urls', namespace='posts')),
    # Страницы авторизации для <<Yatube>>
    path('auth/', include('users.urls')),
    # Страницы авторизации
    path('auth/', include('django.contrib.auth.urls')),
    # Статические страницы
    path('about/', include('about.urls', namespace='about')),
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
