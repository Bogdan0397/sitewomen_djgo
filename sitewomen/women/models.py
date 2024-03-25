from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible


@deconstructible
class RussianValidator:
    ALLOWED_CHARS = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯабвгдеёжзийклмнопрстуфхцчшщбыъэюя0123456789- "
    code = 'russian'

    def __init__(self, message=None):
        self.message = message if message else "Должны присутствовать только русские символы дефиз и пробел"

    def __call__(self, value, *args, **kwargs):
        if not set(value) <= set(self.ALLOWED_CHARS):
            raise ValidationError(self.message, code=self.code)


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Women.Status.PUBLISHED)


class Women(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, db_index=True, unique=True,validators=[
                                                                   MinLengthValidator(5),
                                                                   MaxLengthValidator(100),
                                                                   #RussianValidator()
                                                                                    ])
    content = models.TextField(blank=True, verbose_name="Текст статьи")
    photo = models.ImageField(upload_to='photos/%Y/%m/%d',default=None,null=True,blank=True,verbose_name='Фото')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(choices=tuple(map(lambda x:(bool(x[0]),x[1]),Status.choices)), default=Status.DRAFT, verbose_name="Статус")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name="Категории")
    tags = models.ManyToManyField('TagPost', related_name='tags', verbose_name="Тэги")
    husband = models.OneToOneField('Husband', on_delete=models.SET_NULL, null=True, blank=True, related_name='wuman',verbose_name="Муж")
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL,null = True, related_name='authors',default=None)
    objects = models.Manager()
    published = PublishedManager()
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-time_create']
        verbose_name = 'Известные женщины'
        verbose_name_plural = 'Известные женщины'
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})


class Category(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})



class TagPost(models.Model):
    tag = models.CharField(max_length=100,db_index=True)
    slug = models.SlugField(max_length=255,unique=True,db_index=True)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})


class Husband(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True)
    m_count = models.IntegerField(blank=True,default=0)

    def __str__(self):
        return self.name


class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')