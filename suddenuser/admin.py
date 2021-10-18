from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MatchSudden
from .forms import UserAdminCreationForm,UserAdminChangeForm

admin.site.register(User)
admin.site.register(MatchSudden)

