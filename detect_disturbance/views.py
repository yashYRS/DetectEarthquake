from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages

from .models import Videos


def save_uploaded_video(request):
    curr_title = request.POST['title']
    curr_video = request.POST['video']
    if curr_video and curr_title:
        content = Videos(title=curr_title,
                         video=curr_video)
        content.save()
        messages.success(request, f"Video Saved: {curr_title}")
    else:
        # Enter Message box, showing that no video has been chosen
        messages.error(request, f"Error while saving video")


def index(request):
    context = {}
    print(" I monitored something ")
    if request.method == 'POST':
        if 'bg_video' in request.POST:
            save_uploaded_video(request)
            # Call function to analyze video

        elif 'animal_video' in request.POST:
            save_uploaded_video(request)
            # Call function to monitor entry and exit in video

        elif 'animal_webcam' in request.POST:
            # Call function to open webcam and analyze entry and exit
            pass
    return render(request, 'monitor.html', context)


def visualize(request):
    videos = Videos.objects.all()
    context = {'videos': videos}
    return render(request, 'visualize.html', context)
