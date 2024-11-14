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


class WomenHome(DataMixin, TemplateView):
    template_name = 'women/index.html'
    cat_selected = 0
    title_page = 'Главная страница'

    #
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = get_womenlist_api()
        return context


@login_required
def about(request):
    contact_list = Women.published.all()
    paginator = Paginator(contact_list,3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'women/about.html', {'title':'О сайте','page_obj':page_obj})



class AddPage(LoginRequiredMixin,DataMixin, FormView):
    form_class = AddPostForm
    template_name = 'women/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Добавление статьи'

    def form_valid(self, form):
        c_data = form.cleaned_data

        api_url = 'http://127.0.0.1:8001/api/v1/women/'
        photo_file = self.request.FILES.get('photo')

        data = {**c_data}
        data.pop('photo', None)
        headers = {'Content-Type': 'application/json'}
        files = {'photo': photo_file} if photo_file else None
        response = requests.post(api_url, data=data, files=files)

        if response.status_code == 200:
            pass
        else:
            try:
                error_message = response.json().get('error', 'Не удалось извлечь ошибку')
            except ValueError:
                error_message = response.text

        return super().form_valid(form)


@permission_required(perm='women.view_women',raise_exception=True)
def contact(request):
    return HttpResponse("Обратная связь")


def login(request):
    return HttpResponse("Авторизация")





class ShowPost(DataMixin, DetailView):
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post_slug = self.kwargs[self.slug_url_kwarg]
        self.post = get_womenpost_api(post_slug)
        print(self.post)
        return self.post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=self.post['title'],cat_selected = self.post['categ']['id'])



def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена<h1>')


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