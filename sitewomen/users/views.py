import json
import time

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
import requests
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import CreateView, UpdateView, FormView
from sitewomen import settings
from users.forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm, UserPasswordForm
from users.models import User


class LoginUser(FormView):
        form_class = LoginUserForm
        success_url = reverse_lazy('home')
        template_name = 'users/login.html'
        extra_context = {'title': 'Авторизация'}


        def form_valid(self, form):
            api_url = 'http://127.0.0.1:8001/api/v1/token/'
            c_data = form.cleaned_data
            response = requests.post(api_url, data=c_data)

            if response.status_code == 200:
                # Аутентификация через API успешна, получаем токен (или другие данные)
                token = response.json().get('access')  # Предположим, что токен возвращается в формате JSON

                # Залогиниваем пользователя в Django
                response_token = requests.post('http://127.0.0.1:8001//api/v1/token/verify/',data={'token':token})
                if response_token.json() == {}:

                    user = User.objects.create(username=c_data.get('username'))
                    user.set_password(c_data.get('password'))


                    user.save()
                    if user is not None:
                        login(self.request,user,backend='django.contrib.auth.backends.ModelBackend')

            else:
                    form.add_error(None, 'Неправильный логин или пароль')
                    return self.form_invalid(form)

            return redirect('home')

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.pk)
        logout(request)
        User.delete(user)

        # Дополнительные действия, которые вы можете выполнить перед перенаправлением
        return redirect('home')  # Перенаправляем на нужную страницу после выхода


# def login_user(request):
#     if request.method == 'POST':
#         form = LoginUserForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, username=cd['username'], password=cd['password'])
#             if user and user.is_active:
#                 login(request, user)
#                 return redirect('home')
#     else:
#         form = LoginUserForm()
#     return render(request, 'users/login.html', {'form':form})


class RegisterUser(FormView):
    template_name = 'users/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('users:login')
    extra_context = {'title':'Регистрация'}


    def form_valid(self, form):
        c_data = form.cleaned_data
        api_url = 'http://127.0.0.1:8001//api/v1/users/'
        c_data.pop('password2', None)
        response = requests.post(api_url, data=c_data)

        if response.status_code == 200:
            # Обработка успешного ответа
            pass
        else:
            try:
                # Попытайтесь извлечь ошибку из JSON
                error_message = response.json().get('error', 'Не удалось извлечь ошибку')
            except ValueError:
                # Если JSON не удалось распарсить, используйте текстовое представление ответа
                error_message = response.text

        return super().form_valid(form)

# def register(request):
#     if request.method == 'POST':
#         form = RegisterUserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()
#             return render(request, 'users/register_done.html')
#     else:
#         form = RegisterUserForm()
#     return render(request, 'users/register.html', {'form':form})

class ProfileUser(View):
    template_name = 'users/profile.html'
    # form_class = ProfileUserForm
    success_url = reverse_lazy('users:profile')
    # extra_context = {'title':"Профиль пользователя",'default_img':settings.DEFAULT_USER_IMAGE}


    def get_user_pk(self,users,user):
        for i in users.json():
            if i['username'] == user.username:
                return i['id']
        raise ValueError('User not found')
    def get(self,request):
        users = requests.get('http://127.0.0.1:8001/api/v1/users/')
        pk = self.get_user_pk(users, self.request.user)
        response = requests.get(f'http://127.0.0.1:8001/api/v1/user/{pk}/')
        data = response.json()

        photo_url = data.get('photo')
        if photo_url:
            photo_response = requests.get(photo_url)
            print(photo_response)
            if photo_response.status_code == 200:
                # Сохраняем фотографию пользователя
                self.request.user.photo = photo_response

        form = ProfileUserForm(data)
        form.fields['username'].widget.attrs['disabled'] = 'disabled'
        form.fields['email'].widget.attrs['disabled'] = 'disabled'
        return render(request, self.template_name,{'form':form,'object':data,'title':"Профиль пользователя",'default_img':settings.DEFAULT_USER_IMAGE})

    def patch(self,request):
        users = requests.get('http://127.0.0.1:8001/api/v1/users/')

        pk = self.get_user_pk(users,self.request.user)
        form = ProfileUserForm(request.POST)
        print(form.data)
        if form.is_valid():
            api_url = f'http://127.0.0.1:8001/api/v1/user/{pk}/'
            updated_data = form.cleaned_data
            photo_file = self.request.FILES.get('photo')
            data = {**updated_data}
            data.pop('photo')
            data.pop('username')
            data.pop('email')
            files = {'photo': photo_file} if photo_file else None
            response = requests.patch(api_url, data=data,files=files)

            if response.status_code == 200:
                return redirect('users:profile')
            else:
                print(response.status_code)
                return HttpResponse('Error', status=response.status_code)
        else:
            return HttpResponse('Form data is not valid', status=400)

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'post':
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


    # def post(self,request):
    # def form_valid(self, form):
    #     c_data = form.cleaned_data
    #     api_url = 'http://127.0.0.1:8001/api/v1/user/'
    #     c_data.pop('password2', None)
    #     response = requests.post(api_url, data=c_data)
    #
    #     if response.status_code == 200:
    #         # Обработка успешного ответа
    #         pass
    #     else:
    #         try:
    #             # Попытайтесь извлечь ошибку из JSON
    #             error_message = response.json().get('error', 'Не удалось извлечь ошибку')
    #         except ValueError:
    #             # Если JSON не удалось распарсить, используйте текстовое представление ответа
    #             error_message = response.text
    #
    #     return super().form_valid(form)

class UserPasswordChange(PasswordChangeView):
    template_name = 'users/password_change_form.html'
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')

    def get_user_pk(self, users, user):
        for i in users.json():
            if i['username'] == user.username:
                return i['id']
        raise ValueError('User not found')

    def form_valid(self, form):
        # Вызываем сначала метод из родительского класса, чтобы изменить пароль в базе данных Django
        users = requests.get('http://127.0.0.1:8001/api/v1/users/')
        pk = self.get_user_pk(users, self.request.user)

        api_url = f'http://127.0.0.1:8001/api/v1/user/{pk}/'

        # Получаем новый пароль из формы
        new_password = form.cleaned_data['new_password1']
        response = requests.patch(api_url,data={'password':new_password})
        if response.status_code == 200:
            return redirect('users:logout')
        else:
            raise ValidationError('Не удалось изменить пароль')
        # Отправляем запрос к вашему API для получения информации о пользователе по username


        # Проверяем успешность запроса к API


        return super().form_valid(form)


class UserResetView(PasswordResetView):
    email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")
    response_data = ''

    def form_valid(self, form):

        email_form = self.request.POST.get('email')

        # Получаем новый пароль из форм
        # Отправляем запрос к вашему API для получения информации о пользователе по email
        api_url = f'http://127.0.0.1:8001/api/v1/username/{email_form}/'
        api_response = requests.get(api_url)
        UserResetView.response_data = api_response.json()


        # Проверяем успешность запроса к API
        if api_response.status_code == 200:
            email_data = api_response.json()
            print(email_data)
            if email_data:
                current_site = get_current_site(self.request)
                subject = 'Сброс пароля'
                # Формируем ссылку для сброса пароля, используя uidb64 и token
                email_hash = make_password(email_form + str(time.time()))
                token = urlsafe_base64_encode(force_bytes(email_hash))
                reset_url = f'http://{current_site.domain}/users/password-reset/{token}/'
                message = f'Вы запросили сброс пароля. Пожалуйста, перейдите по следующей ссылке: {reset_url}'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email_form]
                # Отправляем письмо
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            else:
                return HttpResponse('Email not found in API response')
        else:
            return self.form_invalid(form)
        return super().form_valid(form)


class UserPasswordResetConfirm(FormView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy("users:password_reset_complete")
    form_class = UserPasswordForm



    def form_valid(self, form):

        password_form = form.cleaned_data['new_password2']

        # Получаем новый пароль из форм
        # Отправляем запрос к вашему API для получения информации о пользователе по email
        api_url = f'http://127.0.0.1:8001/api/v1/user/{UserResetView.response_data["id"]}/'
        headers = {'Content-type': 'application/json'}
        api_response = requests.put(api_url,json={"password":password_form},headers=headers)


        # Проверяем успешность запроса к API


        return super().form_valid(form)


