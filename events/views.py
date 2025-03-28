import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Event


@login_required
def events_list(request):
    events = Event.objects.filter(end_at__gte=datetime.date.today()).order_by(
        "start_at"
    )

    return render(request, "events/events.jinja", {"events": events})
