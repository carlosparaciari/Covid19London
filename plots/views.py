from django.http import HttpResponse

def index(request):
        return HttpResponse("Dummy page for plots.")
