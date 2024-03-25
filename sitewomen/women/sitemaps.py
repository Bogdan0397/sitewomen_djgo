from django.contrib.sitemaps import Sitemap

from women.api import get_womenpublished_api
from women.models import Women


class PostSiteMap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return get_womenpublished_api()

    def lastmod(self, obj):
        return obj.time_update