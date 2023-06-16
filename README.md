# проект Foodrgam
Сайт Foodgram, «Продуктовый помощник» - это онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Стек технологий:
Python 3.10, Django 4.2, DRF, Djoser, PostgreSQL, Ubuntu, Docker, Docker-compose, nginx, gunicorn

## Развертывание проекта

Клонирование репозитория:
```
git clone git@github.com:ElenaL1/foodgram-project-react/
```
В папке infra создать файл .env, в в котором должны содержаться следующие переменные окружения:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
SECRET_KEY=key
```

Запуск docker-compose из папки infra:
```
docker-compose up -d --build
```

В контейнере `backend`  выполнить миграции, импортировать базу, создать суперпользователя и собрать статику:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py csv_to_bd
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input 
```
Проект доступен по адресу http://localhost/.
zali3.ddns.net

###Примеры запросов к базе:
Пример POST-запроса на опубликование рецепта: POST ... /api/recipes/
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
Более подробно информацию об эндпоинтах и примерах запросов и ответов можно посмотреть в 
[http://localhost/api/docs/](http://localhost/api/docs/redoc.html)

###
Автор проекта: Елена Ламберт

