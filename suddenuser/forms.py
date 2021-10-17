from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField


User = get_user_model()


class UserAdminCreationForm(forms.ModelForm):
    """ Класс формы для создания новых участников."""
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'gender', 'email')

    def clean_password2(self):
        # Проверка введенных паролей на соответствие
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        # Сохраняем переданный пароль в хэш формат
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """ Класс форм для обновления данных участника. """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'gender', 'email')

