from django.http import HttpResponseRedirect

class AdminURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            return HttpResponseRedirect('http://www.mkdjgo.site/admin' + request.path[len('/admin'):])
        return self.get_response(request)