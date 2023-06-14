import csv
import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

# from recipes.models import Ingredient
# from backend.foodgram.settings import BASE_DIR


class Command(BaseCommand):
    """
    Подключаемый модуль manage.py для переноса данных из csv файла в БД.
    Запускается командой из папки backend "python manage.py csv_to_db"
    """
    help = 'Команда для переноса данных из csv файла в БД'

    def handle(self, *args, **options):
        with open(os.path.join(os.path.dirname(settings.BASE_DIR),
                  'data', 'ingredients.csv'),
                  encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file,
                                    fieldnames=['name', 'measurement_unit'])
            Ingredient = apps.get_model('recipes', 'Ingredient')
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'])

        print('Данные из csv файла занесены в базу!')
