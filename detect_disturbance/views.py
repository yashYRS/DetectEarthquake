import datetime

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone


from .models import Videos
from .video_utils import detect_discrepancy, monitor_frame_presence


def save_uploaded_video(request):
    curr_title = request.POST['title']
    # print(request.FILES)
    # print(request.FILES.keys())
    curr_video = request.FILES.get('video', 'sample.mp4')
    store_time = datetime.datetime.now(tz=timezone.utc)
    if curr_video and curr_title:
        content = Videos(title=curr_title,
                         video=curr_video,
                         store_time=store_time)
        content.save()
        messages.success(request, f"Video Saved: {curr_title}")
        return True
    else:
        # Enter Message box, showing that no video has been chosen
        messages.warning(request, f"Error while saving video")
        return False


def index(request):
    context = {}
    if request.method == 'POST':
        if 'bg_video' in request.POST:
            if save_uploaded_video(request):
                # Call function to analyze video
                detect_discrepancy(request)

        elif 'animal_video' in request.POST:
            if save_uploaded_video(request):
                # Call function to monitor entry and exit in video
                monitor_frame_presence(request)

        elif 'animal_webcam' in request.POST:
            # Call function to open webcam and analyze entry and exit
            monitor_frame_presence(request, webcam=True)
    return render(request, 'monitor.html', context)


def visualize(request):
    videos = Videos.objects.all()
    context = {'videos': videos}
    return render(request, 'visualize.html', context)
