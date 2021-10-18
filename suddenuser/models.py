from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from .manager import UserManager
from django.utils.translation import gettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.mail import send_mail, send_mass_mail


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
    avatar = models.ImageField(upload_to="participants/avatar/", blank=True, null=True,
                               verbose_name="Аватар участника")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регестрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    is_active = models.BooleanField(default=True, verbose_name="Статус активности")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ к админ панели")
    is_admin = models.BooleanField(default=False, verbose_name="Права администратора")

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender', 'avatar']

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ('-created_at', '-updated_at',)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        if self.avatar:
            img = Image.open(self.avatar)
            watermark = Image.open('/home/leom/PycharmProjects/suddenMeetProject/pepe.png')
            img.paste(watermark, (0,0))
            output = BytesIO()
            img.save(output, 'PNG', optimize=True)
            output.seek(0)
            self.avatar.file = output
        super().save(*args, **kwargs)


class MatchSudden(models.Model):
    """ Класс для сбора данных о симпатиях участников. """
    mover = models.OneToOneField(User, related_name='mover', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Участник")
    simpy = models.OneToOneField(User, related_name='simpy', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Симпатия")

    def __str__(self):
        return f"{self.mover.first_name} оценил {self.simpy.first_name}"

    def mutual_sympathy(self):
        # Метод проверки на взаимную симпатию
        all_match = MatchSudden.objects.all()
        try:
            all_match.get(mover=self.simpy, simpy=self.mover)
            message1 = ('Взаимность', f'Вы понравились {self.simpy.first_name}! Почта участника: {self.simpy.email}',
                        'localhost@gmail.com', [self.mover.email])
            message2 = ('Взаимность', f'Вы понравились {self.mover.first_name}! Почта участника: {self.mover.email}',
                        'java.leon@mail.ru', [self.simpy.email])
            send_mass_mail((message1, message2), fail_silently=False)
            return "Ого это взаимно нечего себе!"
        except ObjectDoesNotExist:
            return "Надеюсь это будет взаимно"

