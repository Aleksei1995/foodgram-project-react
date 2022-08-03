from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField('Логин', max_length=150,
                                unique=True,
                                blank=False,
                                null=False,
                                )
    email = models.EmailField('Адрес электронной почты',
                              max_length=254,
                              unique=True,
                              blank=False,
                              null=False
                              )
    first_name = models.CharField('Имя', max_length=150, blank=False)
    last_name = models.CharField('Фамилия', max_length=150, blank=False)
    password = models.CharField('Пароль', max_length=150, blank=False)

    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='user_author'),
            models.CheckConstraint(check=~models.Q(user=models.F('author')),
                                   name='user_not_author')
        ]

    def __str__(self):
        return (f'Пользователь {self.user}'
                f' подписан на автора рецепта {self.author}')
