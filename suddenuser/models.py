from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from .manager import UserManager
from django.utils.translation import gettext_lazy as _
from PIL import Image


def watermark_photo(input_image_path, output_image_path, watermark_image_path, position):
    base_image = Image.open(input_image_path)
    watermark = Image.open(watermark_image_path)
    width, height = base_image.size

    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(base_image, (0, 0))
    transparent.paste(watermark, position, mask=watermark)
    transparent.show()
    transparent.save(output_image_path)


class User(AbstractBaseUser):
    """ Модель участников которая создана на основе пользовательской модели """

    class GenderChoice(models.TextChoices):
        MALE = "М", _("Мужской")
        FEMALE = "Ж", _("Женский")

    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя участника")
    last_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Фамилия участника")
    gender = models.CharField(max_length=20, null=True, blank=True,
                              choices=GenderChoice.choices, verbose_name="Пол участника")
    email = models.EmailField(unique=True, verbose_name="Электронный адрес участника")
    avatar = models.ImageField(upload_to="media/participants/avatar/", blank=True, null=True,
                               verbose_name="Аватар участника")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регестрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    is_active = models.BooleanField(default=True, verbose_name="Статус активности")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ к админ панели")
    is_admin = models.BooleanField(default=False, verbose_name="Права администратора")

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender', 'avatar']

    object = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ('-created_at', '-updated_at', )

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

