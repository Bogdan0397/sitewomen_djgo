import random

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.deconstruct import deconstructible
from simplemathcaptcha.fields import MathCaptchaField

from .api import get_cats_api, get_husbands_api
from .models import Category, Husband, Women


@deconstructible
class RussianValidator:
    ALLOWED_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщбыъэюя0123456789- "
    code = 'russian'

    def __init__(self, message=None):
        self.message = message if message else "Должны присутствовать только русские символы дефиз и пробел"

    def __call__(self, value, *args, **kwargs):
        if not set(value) <= set(self.ALLOWED_CHARS):
            raise ValidationError(self.message, code=self.code)

class AddPostForm(forms.Form):
    title = forms.CharField(label='Название',max_length=255,required=True)
    slug = forms.SlugField(label='Слаг',required=True)
    photo = forms.ImageField(label='Фото',required=False)
    content = forms.CharField(label='Контент',required=True)
    is_published = forms.BooleanField(initial=False,required=False,label='Опубликовано')
    CHOICES1 = [(i['id'],i['name']) for i in get_cats_api()]
    cat = forms.ChoiceField(choices=CHOICES1, label='Категория')
    CHOICES2 = [(i['id'],i['name']) for i in get_husbands_api()]
    CHOICES2.append((None,None))
    husband = forms.ChoiceField(choices =CHOICES2,  required=False,  label='Муж')
    #
    #
    # class Meta:
    #     model = Women
    #     fields = ['title', 'slug','photo', 'content', 'is_published', 'cat', 'husband', 'tags']
    #     widgets = {
    #         'title': forms.TextInput(attrs={'class': 'form-input'}),
    #         'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
    #     }
    #     lables = {'slug':'URL'}
    #     #empty_lables = {'title':'Категория не выбрана'} ???????


    # def clean_title(self):
    #     title = self.cleaned_data['title']
    #     ALLOWED_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщбыъэюя0123456789- "
    #
    #     if not set(title) <= set(ALLOWED_CHARS):
    #         raise ValidationError("Должны присутствовать только русские символы дефиз и пробел")
    #     elif len(title)>50:
    #         raise ValidationError('Длина строки больше 50 символов')
    #
    #     return title
    #


class ContactForm(forms.Form):
    name = forms.CharField(label='Имя',max_length=255)
    email = forms.EmailField(label='Email')
    content= forms.CharField(widget=forms.Textarea(attrs={'cols':60,'rows':10}))
    captcha = MathCaptchaField()


class UploadFileForm(forms.Form):
    file = forms.ImageField(label='Файл')