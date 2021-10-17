from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """ Менеджер для модели участников """

    def create_user(self, email, first_name, last_name, gender, avatar,
                    password=None, is_staff=None, is_admin=False, is_activate=True):
        # Общая функция при создании участника
        if not email:
            raise ValueError("У участника должен быть электронная почта")
        if not first_name:
            raise ValueError("У участника должно быть имя")
        if not last_name:
            raise ValueError("У участника должна быть фамилия")
        if not password:
            raise ValueError('У участника должен быть пароль')

        user_obj = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            avatar=avatar,
        )
        user_obj.set_password(password)
        user_obj.is_staff = is_staff
        user_obj.is_admin = is_admin
        user_obj.is_activate = is_activate
        user_obj.save(using=self.db)

    def create_superuser(self, email, first_name, last_name, gender=None, avatar=None, password=None):
        # Функция которая выполняется при создании суперпользователя
        user = self.create_user(
            email,
            first_name,
            last_name,
            gender=gender,
            avatar=avatar,
            password=password,
            is_staff=True,
            is_admin=True
        )
        return user
