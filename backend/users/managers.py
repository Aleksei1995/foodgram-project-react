from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password, username):

        email = self.normalize_email(email)
        user = self.model(email=email,
                          username=username,
                          first_name=first_name,
                          last_name=last_name)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, first_name, last_name, password,
                         username):

        user = self.create_user(email, first_name, last_name, password,
                                username)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
