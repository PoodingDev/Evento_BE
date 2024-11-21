from django.http import HttpResponse

def event_home(request):
    return HttpResponse("This is the event app homepage.")
