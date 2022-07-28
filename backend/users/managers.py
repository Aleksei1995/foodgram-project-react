from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password, username):
        """ Создает и возвращает пользователя. """
        if username is None:
            raise TypeError('Обязательное поле.')

        if email is None:
            raise TypeError('Обязательное поле.')

        if first_name is None:
            raise TypeError('Обязательное поле.')

        if last_name is None:
            raise TypeError('Обязательное поле.')

        if password is None:
            raise TypeError('Обязательное поле.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, first_name, last_name, password,
                         username):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, first_name, last_name, password,
                                username)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
