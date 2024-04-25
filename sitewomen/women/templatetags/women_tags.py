from django import template
from django.db.models import Count
from datetime import datetime

from django.urls import reverse

import women.views as views
from women.api import get_womenlist_api, get_tags_api
from women.models import Category, TagPost

register = template.Library()


@register.inclusion_tag('women/list_categories.html')
def show_categories(cat_selected = 0):
    cats = Category.objects.annotate(total=Count('posts')).filter(total__gt=0)
    return {'cats':cats,'cat_selected':cat_selected}


@register.inclusion_tag('women/list_tags.html')
def show_all_tags():
    return {'tags':get_tags_api()}


@register.inclusion_tag('women/datetime.html')
def date_convert(post_id):
    p = get_womenlist_api()
    res = []
    for i in p:
        for j in i.keys():
            if j == 'time_update':
                res.append(i[j])
    res = [datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y/%m/%d") for i in res]

    index = 0
    if int(post_id)<=17:
        index = int(post_id)-1
    else:
        index = int(post_id)-11
    return {'post':res[int(post_id)-1]}


#absolute_urls
@register.simple_tag
def get_absolute_url_for_api_post(api_post):
    return reverse('post', kwargs={'post_slug': api_post['slug']})

@register.simple_tag
def get_absolute_url_for_api_tag(slug):
    return reverse('tag', kwargs={'tag_slug': slug})
