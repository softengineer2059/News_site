from django.views.generic import ListView, FormView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import *
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage




class Account(ListView):
    model = Profile
    template_name = "profile.html"


class Login(LoginView):

    form_class = LoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('main')


class Logout(LogoutView):

    next_page = "main"


class Register(FormView):

    form_class = UserRegister
    success_url = reverse_lazy('main')
    template_name = "register.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


@login_required
def change_base_info(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
    else:
        form = UserUpdateForm(instance=request.user)
    return redirect('profile')


class ChangePasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(current_password):
            messages.error(request, 'Не правильно введен текущий пароль')
            return redirect('profile')

        elif new_password1 != new_password2:
            messages.error(request, 'Пароли введеные в поле 1 и 2 не совпадают')

        elif len(new_password1) < 8:
            messages.error(request, 'Пароль должен содержать не менее 8 символов')
            return redirect('profile')

        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Пароль успешно изменен!')

        return redirect('profile')


def upload_avatar_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Получаем новое изображение
        new_image = request.FILES['image']

        # Удаляем старую аватарку, если она существует
        try:
            old_avatar = Profile.objects.get(user=request.user)
            if old_avatar.avatar:
                # Удаляем файл из файловой системы
                default_storage.delete(old_avatar.avatar.path)
            # Удаляем запись из базы данных
            old_avatar.delete()
        except Profile.DoesNotExist:
            pass  # У пользователя не было аватарки

        # Создаем новую запись с новым изображением
        Profile.objects.create(user=request.user, avatar=new_image)

        return redirect('profile')

    return redirect('profile')  # Если не POST-запрос или нет файла


@receiver(pre_delete, sender=Profile)
def delete_avatar_file(sender, instance, **kwargs):
    if instance.avatar:
        instance.avatar.delete(save=False)