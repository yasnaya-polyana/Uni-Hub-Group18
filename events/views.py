from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def events_list(request):
    return render(request, 'events/events.html') 