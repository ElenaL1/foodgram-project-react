# Generated by Django 4.2.1 on 2023-06-19 09:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed', to=settings.AUTH_USER_MODEL, verbose_name='автор рецепта')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='подписчик')),
            ],
            options={
                'verbose_name': 'подписка',
                'verbose_name_plural': 'подписки',
            },
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.UniqueConstraint(fields=('user', 'following'), name='unique_user_following'),
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.CheckConstraint(check=models.Q(('user', models.F('following')), _negated=True), name='unique_following'),
        ),
    ]
