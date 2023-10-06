# Yatube

Yatube - социальная сеть, созданная в рамках учебного курса Яндекс.Практикум.
Yatube дает пользователям возможность создать учетную запись, публиковать посты и подписываться на любимых авторов. Посты могут быть привязаны к тематической группе, на которую также можно подписаться.

## Стек технологий
- проект написан на Python с использованием веб-фреймворка Django.
- работа с изображениями - sorl-thumbnail, pillow
- система управления версиями - git
- база данных - SQLite

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
    git clone https://github.com/94R1K/hw05_final.git
```
```
    cd hw05_final
```
Cоздать и активировать виртуальное окружение:
```
    python3 -m venv env
```
```
    source env/bin/activate
```
```
    python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
    pip install -r requirements.txt
```
Выполнить миграции:
```
    python3 manage.py migrate
```
Создайте суперпользователя:
```
    python3 manage.py createsuperuser
```
Запустить проект:
```
    python3 manage.py runserver
```
____
Ваш проект запустился на http://127.0.0.1:8000/  
C помощью команды pytest вы можете запустить тесты и проверить работу модулей

# Об авторе
Лошкарев Ярослав Эдуардович \
Python-разработчик (Backend) \
Россия, г. Москва \
E-mail: real-man228@yandex.ru 

[![VK](https://img.shields.io/badge/Вконтакте-%232E87FB.svg?&style=for-the-badge&logo=vk&logoColor=white)](https://vk.com/yalluv)
[![TG](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/yallluv) 
