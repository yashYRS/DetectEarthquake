import cv2
import imutils
import datetime
import numpy as np
from pathlib import Path


from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from .models import FramePresence, Videos


def draw_lines(img, lines):
    for line in lines:
        coords = line[0]
        cv2.line(img, (coords[0], coords[1]),
                 (coords[2], coords[3]), [0, 255, 0], 3)


def check_lines(ave_list):
    same_lines = 0
    lines1, lines2 = ave_list
    for line1 in lines1:
        pts = line1[0]
        for line2 in lines2:
            cords = line2[0]
            if (pts[0] == cords[0] and pts[1] == cords[1] and pts[2] == cords[2] and pts[3] == cords[3]):
                same_lines = same_lines + 1
    return same_lines


def save_entry_exit(request, entry, exit):

    try:
        content = FramePresence(entry_time=entry, exit_time=exit)
        content.save()
        messages.info(request, "Captured frame presence")
    except Exception as e:
        # Enter Message box, showing that no video has been chosen
        messages.warning(request, f"Error while saving frame presence")


def detect_discrepancy(request, sensitivity=50):
    """
    The nmber of common lines between 2 consecutive frames is high but as the
    earthquake starts, due to the shifting of the lines, the average keeps
    dropping due to the constant shaking of everything, and a alert is issued

    Assumptions -
        Lanes are demarkated by white color
        if not, apt color can be given to InRange function...

    Args:
        request (TYPE): Request object returned by the form
        sensitivity (int, optional): After which lines are said to differ

    """
    video_obj = Videos.objects.latest('store_time')
    title = video_obj.title
    base_dir = Path(settings.BASE_DIR)
    video_path = Path(video_obj.video.url)
    file_name = str(base_dir / video_path.relative_to(video_path.anchor))
    print(file_name, "File location", title, " Title")

    frame_no, ave_same, ave_list = 0, 0, list()
    cap = cv2.VideoCapture(file_name)

    while True:

        ret, frame = cap.read()
        frame_no = frame_no + 1
        if not ret or frame is None:
            break
        cv2.imshow(title, frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # detecting white lanes of a road ....
        lower_white = np.array([0, 0, 255 - sensitivity])
        upper_white = np.array([255, 255 - sensitivity, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        edges = cv2.Canny(mask, 75, 150)
        edges = cv2.GaussianBlur(edges, (5, 5), 0)
        try:
            # detected lines
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=20)
            ave_list.append(lines)
            # lines detected are drawn to the frames...
            draw_lines(frame, lines)
            if (frame_no % 2 == 0 and len(lines) > 0):
                # do this if lines were detected...
                same = check_lines(ave_list)
                ave_list = []
                # computing the average
                ave_same = (ave_same*(frame_no/2 - 1) + same) / (frame_no/2)
        # if the number of same lines falls below a threshold and
        # lines are being detected (i.e not due to traffic) ->
        # high chance of an earthquake
                if same < 5 and len(lines) > 10:
                    message.error(request, f"Video: {title} needs ATTENTION")
                    break
        # # if average needs to be verified, uncomment these lines
        # if (frame_no%50 == 0 ) :
        #     print(ave_same)
        except Exception as e:
            pass
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyWindow(title)


def monitor_frame_presence(request, webcam=False, min_area=1500):
    # Monitor the webcam / the video entered
    if webcam:
        vs = cv2.VideoCapture(0)
        title = "Webcam"
    else:
        video_obj = Videos.objects.latest('store_time')
        title = video_obj.title
        base_dir = Path(settings.BASE_DIR)
        video_path = Path(video_obj.video.url)
        file_name = str(base_dir / video_path.relative_to(video_path.anchor))
        print(file_name, "File location", title, " Title")
        vs = cv2.VideoCapture(file_name)

    # initialize the first frame in the video stream
    first_frame, prev_status = None, 0
    # loop over the frames of the video
    while True:
        # grab the current frame and initialize the occupied/unoccupied
        ret, frame = vs.read()
        if not ret or frame is None:
            break

        text, occupied = "Unoccupied", 0

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the first frame is None, initialize it
        if first_frame is None:
            first_frame = gray
            continue

        # compute the absolute difference between the current and first frame
        frameDelta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        # find contours on thresholded image
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[0]

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < min_area:
                continue
            # Contour big enough, hence something is occupying the frame
            if occupied == 0:
                occupied = 1
            # compute the bounding box for the contour
            (x, y, w, h) = cv2.boundingRect(c)
            # draw it on the frame, and update the text
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

        # draw the text and timestamp on the frame
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame,
                    datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)

        # show the frame and record if the user presses a key
        cv2.imshow(title, frame)

        # if the `q` key is pressed, break from the lop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if prev_status != occupied:
            if occupied == 0:
                exit_time = datetime.datetime.now(tz=timezone.utc)
                print("frame exit: ", exit_time)
                save_entry_exit(request, entry_time, exit_time)
            else:
                entry_time = datetime.datetime.now(tz=timezone.utc)
                print("frame entry: ", entry_time)
        # prev_status of frames updated
        prev_status = occupied

    # cleanup the camera and close any open windows
    cv2.destroyWindow(title)
