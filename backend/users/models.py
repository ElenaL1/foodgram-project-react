from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

User = get_user_model()


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="подписчик",
        related_name="follower"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="автор рецепта",
        related_name="followed"
    )

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        constraints = [
            UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'),
            CheckConstraint(
                check=~Q(user=F('following')),
                name='unique_following')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
