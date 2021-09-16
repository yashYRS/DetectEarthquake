from django.db import models


class FramePresence(models.Model):
    # Captures the Entry and Exit of objects from the screen
    entry_time = models.DateTimeField("Entry Time")
    exit_time = models.DateTimeField("Exit Time")


class Videos(models.Model):
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='detect_disturbance/')
    store_time = models.DateTimeField("Storage Time")

    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'

    def __str__(self):
        return self.title
