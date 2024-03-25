import requests
from django.http import Http404


def get_womenlist_api():
    url = 'http://www.mkdjgo.site/api/v1/women/'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


def get_womenpost_api(post_slug):
    url = f'http://www.mkdjgo.site/api/v1/women/{post_slug}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Post not found")


def get_womencat_api(cat_slug):
    url = f'http://www.mkdjgo.site/api/v1/womencatlist/{cat_slug}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Category does not exist")


def get_womentag_api(tag):
    url = f'http://www.mkdjgo.site/api/v1/womentaglist/{tag}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Tag does not exist")

def get_tags_api():
    url = f'http://www.mkdjgo.site/api/v1/taglist'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Tag does not exist")

def get_cats_api():
    url = f'http://www.mkdjgo.site/api/v1/catlist'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Not Found")

def get_husbands_api():
    url = f'http://www.mkdjgo.site/api/v1/husbandslist'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Not Found")


def get_womenpublished_api():
    url = f'http://www.mkdjgo.site/api/v1/womenpublished'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Not Found")


def get_user_model_api():
    url = f'http://www.mkdjgo.site/api/v1/users'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Http404("Not Found")