from django.http import HttpResponse

def calendar_home(request):
    return HttpResponse("This is the calendar app homepage.")
