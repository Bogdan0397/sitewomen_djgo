import datetime


from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

from women.api import get_user_model_api


class LoginUserForm(forms.Form):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class':'form-input'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    # class  Meta:
    #     model = get_user_model()
    #     fields = ['username', 'password']


class RegisterUserForm(forms.Form):
    username = forms.CharField(label='Логин',widget=forms.TextInput(attrs={'class':'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email',widget=forms.TextInput(attrs={'class':'form-input'}))
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'class':'form-input'}))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-input'}))


        # class Meta:
        # fields = ['username', 'email', 'first_name', 'last_name','password1', 'password2']
        # labels = {'email': 'Email',
        #           'first_name': 'Имя',
        #           'last_name':'Фамилия',
        #           }
        #
        # widgets = {'email': forms.TextInput(attrs={'class':'form-input'}),
        #           'first_name': forms.TextInput(attrs={'class':'form-input'}),
        #           'last_name':forms.TextInput(attrs={'class':'form-input'})}

    # def save(self):
    #     # Здесь вы можете реализовать логику сохранения данных через ваше API
    #     username = self.cleaned_data['username']
    #     email = self.cleaned_data['email']
    #     first_name = self.cleaned_data['first_name']
    #     last_name = self.cleaned_data['last_name']
    #     password = self.cleaned_data['password1']  # Обратите внимание, что это не безопасно
    #     # Отправить данные в API для создания пользователя
    #     create_user_in_api(username, email, first_name, last_name, password)

    #Вернути із апі список імейлів
    def clean_email(self):
        email = self.cleaned_data['email']
        for i in get_user_model_api():
            if email in i.values():
                raise forms.ValidationError('Такой Email уже существует')
        return email

class ProfileUserForm(forms.Form):
    username = forms.CharField(required=False,label='Логин',widget=forms.TextInput(attrs={'class':'form-input'}))
    email = forms.CharField(required=False, label='Email', widget=forms.TextInput(attrs={'class': 'form-input'}))
    this_year = datetime.date.today().year
    date_birth = forms.DateField(required=False,widget=forms.SelectDateWidget(years=tuple(range(this_year-100,this_year-5))))
    photo = forms.ImageField(label = 'Photo',required=False)
    first_name = forms.CharField(label='Имя',required=False,widget=forms.TextInput(attrs={'class':'form-input'}))
    last_name = forms.CharField(label='Фамилия', required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=("Текущий пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        strip=False,

    )
    new_password1 = forms.CharField(
        label= ("Новый пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),

    )
    new_password2 = forms.CharField(
        label=("Повторите пароль"),
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )



class UserPasswordForm(forms.Form):
    """
    A form that lets a user set their password without entering the old
    password
    """

    error_messages = {
        "password_mismatch": "The two password fields didn’t match."
    }
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )



    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        password_validation.validate_password(password2)
        return password2
