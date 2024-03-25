import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import requests
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView

from sitewomen import settings
from women.api import get_womenlist_api, get_womenpost_api, get_womencat_api, get_womentag_api
from women.forms import AddPostForm, UploadFileForm, ContactForm
from women.models import Women, Category, TagPost, UploadFiles
from women.utils import DataMixin
from django.core.cache import cache

# menu = [{'title': "О сайте", 'url_name': 'about'},
#         {'title': "Добавить статью", 'url_name': 'add_page'},
#         {'title': "Обратная связь", 'url_name': 'contact'},
#         {'title': "Войти", 'url_name': 'login'}]


# Create your views here.
# def index(request):
#     posts = Women.published.all().select_related('cat')
#     data = {'title': 'Главная страница',
#             'posts': posts,
#             'menu': menu,
#             'cat_selected': 0, }
#
#     return render(request, 'women/index.html', context=data)
#


class WomenHome(DataMixin, TemplateView):
    #model = Women
    template_name = 'women/index.html'
    # context_object_name = 'posts'
    cat_selected = 0
    title_page = 'Главная страница'

    #
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = get_womenlist_api()
        return context

    # def get_queryset(self):
    #     return Women.published.all().select_related('cat')


# import uuid
# def handle_uploaded_file(f):
#     with open(f"uploads/{str(uuid.uuid4())}{f.name}", "wb+") as destination:
#         for chunk in f.chunks():
#             destination.write(chunk)

@login_required
def about(request):
    contact_list = Women.published.all()
    paginator = Paginator(contact_list,3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'women/about.html', {'title':'О сайте','page_obj':page_obj})



# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = AddPostForm()
#
#     data = {'menu': menu, 'title': 'Добавление статьи', 'form': form}
#     return render(request, 'women/addpage.html', data)

class AddPage(LoginRequiredMixin,DataMixin, FormView):
    form_class = AddPostForm
    # model = Women #need CreateView class
    # fields = ['slug','title','content']
    template_name = 'women/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Добавление статьи'
    # permission_required = 'women.add_women'

    # def form_valid(self, form):
    #     w = form.save(commit=False)
    #     w.author = self.request.user
    #     return super().form_valid(form)

    def form_valid(self, form):
        c_data = form.cleaned_data

        api_url = 'http://www.mkdjgo.site/api/v1/women/'
        photo_file = self.request.FILES.get('photo')

        data = {**c_data}  # Используем копирование словаря для избежания модификации исходного словаря
        # Удалите поле 'photo' из данных, чтобы его не было в JSON

        data.pop('photo', None)
        headers = {'Content-Type': 'application/json'}

        files = {'photo': photo_file} if photo_file else None
        response = requests.post(api_url, data=data, files=files)




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


@permission_required(perm='women.view_women',raise_exception=True)
def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")


# def show_post(request, post_slug):
#     post = get_object_or_404(Women, slug=post_slug)
#     data = {'title': post.title,
#             'post': post,
#             'menu': menu,
#             'cat_selected': 0}
#     return render(request, 'women/post.html', data)


class ShowPost(DataMixin, DetailView):
    # model = Women
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        # w_lst = cache.get('women_post')
        # if not w_lst or w_lst.slug != self.kwargs[self.slug_url_kwarg]:
        #     w_lst = get_object_or_404(Women.published,slug = self.kwargs[self.slug_url_kwarg]) #без апи
        #     cache.set('women_post',w_lst,30)
        # return w_lst
        post_slug = self.kwargs[self.slug_url_kwarg]
        self.post = get_womenpost_api(post_slug)
        print(self.post)
        return self.post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=self.post['title'],cat_selected = self.post['categ']['id'])



def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена<h1>')


# def show_category(request, cat_slug):
#     category = get_object_or_404(Category, slug=cat_slug)
#     posts = Women.published.filter(cat_id=category.pk).select_related('cat')
#
#     data = {
#         'title': f'Рубрика: {category.name}',
#         'menu': menu,
#         'posts': posts,
#         'cat_selected': category.pk,
#     }
#     return render(request, 'women/index.html', context=data)

class WomenCategory(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        self.qs = get_womencat_api(self.kwargs['cat_slug'])
        return self.qs

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title='Категория - ' + self.qs[0]['categ']['name'], cat_selected=self.qs[0]['categ']['id'])



# def show_tag_postlist(request, tag_slug):
#     tag = get_object_or_404(TagPost, slug=tag_slug)
#     posts = tag.tags.filter(is_published=Women.Status.PUBLISHED).select_related('cat')
#
#     data = {
#         'title': f'Тег: {tag.tag}',
#         'menu': menu,
#         'posts': posts,
#         'cat_selected': None,
#     }
#
#     return render(request, 'women/index.html', context=data)

class TagShow(DataMixin, ListView):
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        self.taglist = get_womentag_api(self.kwargs['tag_slug'])
        return self.taglist

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        title = ''
        for i in self.taglist[0]['tagpost']:
            if i['slug'] == self.kwargs['tag_slug']:
                title = i['tag']
        return self.get_mixin_context(context, title=title)

class UpdatePage(PermissionRequiredMixin,DataMixin, UpdateView):
    model = Women
    fields = ['title','content','photo','is_published','cat','tags']
    template_name = 'women/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактирование страницы'
    permission_required = 'women.change_women'

class WomenDeleteView(DeleteView):
    model = Women
    success_url = reverse_lazy("home")
    template_name = 'women/delete_form.html'


class ContactFormView(LoginRequiredMixin,DataMixin,FormView):
    form_class = ContactForm
    template_name = 'women/contact.html'
    success_url = reverse_lazy('home')
    title_page = 'Обратная связь'


    def form_valid(self, form):
        email_user = self.request.POST.get('email')
        print(email_user)
        email_admin = settings.EMAIL_HOST_USER
        recipient_list = [email_admin]
        subject = f'From:{email_user}'
        message = self.request.POST.get('content')
        # Отправляем письмо
        email = EmailMessage(subject, message, to=recipient_list, from_email=email_user)
        email.send()
        return super().form_valid(form)