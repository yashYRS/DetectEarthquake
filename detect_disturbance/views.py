from django.http import HttpResponse
from django.shortcuts import render

from .models import Videos


def index(request):
    context = {}
    print(" I monitored something ")
    if request.method == 'POST':

        title = request.POST['title']
        video = request.POST['video']

        content = Videos(title=title, video=video)
        content.save()
        print(" I uploaded something ")
        render(request, 'monitor.html', context)
    return render(request, 'monitor.html', context)


def visualize(request):
    videos = Videos.objects.all()
    context = {'videos': videos}
    return render(request, 'visualize.html', context)
