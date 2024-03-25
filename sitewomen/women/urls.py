from django.urls import path, re_path, register_converter
from . import views
from . import converters
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps.views import sitemap

from .sitemaps import PostSiteMap

register_converter(converters.FourDigitYearConverter, "year4")

sitemaps = {'posts':PostSiteMap}

urlpatterns = [
    path('', cache_page(30)(views.WomenHome.as_view()), name='home'),  # http://127.0.0.1:8000
    path('about/', views.about, name='about'),
    path('addpage/', views.AddPage.as_view(), name='add_page'),
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('login/', views.login, name='login'),
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('category/<slug:cat_slug>/', views.WomenCategory.as_view(), name='category'),
    path('tags/<slug:tag_slug>/', views.TagShow.as_view(),name='tag'),
    path('edit/<slug:slug>/', views.UpdatePage.as_view(),name='update'),
    path('delete/<slug:slug>/', views.WomenDeleteView.as_view(),name='delete'),
    path('sitewomen.xml',cache_page(86400)(sitemap),{'sitemaps':sitemaps}, name = 'django.contrib.sitemaps.views.sitemap')
]
