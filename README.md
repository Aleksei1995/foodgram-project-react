![example workflow](https://github.com/Aleksei1995/foodgram-project-react/actions/workflows/main.yml/badge.svg)
# Foodgram
Foodgram - онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
### Локальный запуск проекта:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Aleksei1995/foodgram-project-react.git
```
Создайте и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/scripts/activate
```
Создайте в директории infra файл .env c параметрами:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Перейдите в директорию backend и установите файл зависимостей requirements.txt:
```
cd backend/
```
```
pip install -r requirements.txt
```
Выполните миграции:
```
python manage.py migrate
```
Запустите сервер:
```
python manage.py runserver
```
### Запуск проекта с Docker:
Установите Docker.
Проверьте файлы docker-compose.yaml и nginx.conf которые находятся в директории infra/.
При необходимости добавьте/измените адреса проекта в файле nginx.conf.
Запустите docker compose:
```
docker-compose up -d --build
```
Должны появиться 4 контейнера: db, backend, frontend, nginx.
Примените миграции:
```
docker-compose exec backend python manage.py migrate
```
Создайте администратора:
```
docker-compose exec backend python manage.py createsuperuser
```
Соберите статику:
```
docker-compose exec backend python manage.py collectstatic --noinput
```
### Сайт:
http://51.250.31.89/
### Стек технологий:
[Python](https://www.python.org/),  [Django](https://www.djangoproject.com/),  [Django REST-Framework](https://www.django-rest-framework.org/),  [PostgresSQL](https://www.postgresql.org/),  [NGINX](https://nginx.org/ru/),  [Gunicorn](https://gunicorn.org/),  [Docker](https://www.docker.com/),  [GitHub](https://github.com/features/actions),  [Yandex.Cloud](https://cloud.yandex.ru/)
