from django.http import HttpResponse
from django.shortcuts import render

from .models import Videos


def save_uploaded_video(post_request):
    curr_title = post_request['title']
    curr_video = post_request['video']
    if curr_video:
        content = Videos(title=curr_title,
                         video=curr_video)
        content.save()
    else:
        # Enter Message box, showing that no video has been chosen
        pass


def index(request):
    context = {}
    print(" I monitored something ")
    if request.method == 'POST':
        if 'bg_video' in request.POST:
            print('Disturbance analyzed')
            save_uploaded_video(request.POST)
            # Call function to analyze video

        elif 'animal_video' in request.POST:
            print('Entry exit analyzed')
            save_uploaded_video(request.POST)
            # Call function to monitor entry and exit in video

        elif 'animal_webcam' in request.POST:
            print('Web cam to be opened')
            # Call function to open webcam and analyze entry and exit

    return render(request, 'monitor.html', context)


def visualize(request):
    videos = Videos.objects.all()
    context = {'videos': videos}
    return render(request, 'visualize.html', context)
