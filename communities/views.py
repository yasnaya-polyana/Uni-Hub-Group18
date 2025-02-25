from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def community_list(request):
    return render(request, 'communities/community_list.html')

@login_required
def community_detail(request, community_id):
    return render(request, 'communities/communities.html')
