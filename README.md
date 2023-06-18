# проект Foodrgam
![foodrgam](https://github.com/ElenaL1/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)

Сайт Foodgram, «Продуктовый помощник» - это онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Стек технологий:
Python 3.10, Django 4.2, DRF, Djoser, PostgreSQL, Ubuntu, Docker, Docker-compose, nginx, gunicorn, Github Actions, Yandex Cloud

## Развертывание проекта
Запуск проекта через Github Actions.

На сервере нужно установить docker и docker-compose. Скопировать на сервер файлы docker-compose.yml и nginx.conf:
```
scp docker-compose.yml <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/docker-compose.yaml
scp default.conf <логин_на_сервере>@<IP_сервера>:/home/<логин_на_сервере>/nginx.conf
```

Далее на сервере нужно запустить следущие команды (выполнить миграции, создать суперпользователя, собрать статитку, загрузить данные):
```
sudo docker-compose exec foodgram_backend python manage.py migrate
sudo docker-compose exec foodgram_backend python manage.py createsuperuser
sudo docker-compose exec foodgram_backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py loaddata fixtures.json -->
```

## Workflow состоит из четырёх шагов:
    Проверка кода на соответствие PEP8 
    Сборка и публикация образа бекенда на DockerHub.
    Автоматический деплой на удаленный сервер.
    Отправка уведомления в телеграм-чат.
Деплой сервера запускается при обновление репозитория (git push).


Проект доступен по [адресу](http://158.160.44.210/)


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
[redoc](http://158.160.44.210/redoc.html)

### Автор проекта: Елена Ламберт

