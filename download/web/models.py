from django.contrib.auth.models import AbstractUser
from django.db import models
import re
from django.core.exceptions import ValidationError
import pytz

class User(AbstractUser):
   pass

class Download(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="downloads")
    format = models.CharField(max_length=3, choices=[('mp3', 'MP3'), ('mp4', 'MP4')])
    link = models.URLField(unique=False)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255, default='default_filename.mp3')

    def clean(self):
        # Validate YouTube URL
        youtube_pattern = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+/|watch\?v=|watch/|shorts/)?'
            r'([^&=%\?]{11})(\S*)'
        )
        if not youtube_pattern.match(self.link):
            raise ValidationError('Invalid YouTube URL')
        # Validate filename extension matches the format
        if self.format == 'mp3' and not self.filename.endswith('.mp3'):
            raise ValidationError('Filename extension does not match the format mp3.')
        elif self.format == 'mp4' and not self.filename.endswith('.mp4'):
            raise ValidationError('Filename extension does not match the format mp4.')

    def save(self, *args, **kwargs):
        # Call clean method to enforce validation rules
        self.clean()
        super().save(*args, **kwargs)

    
    
    def serialize(self):
        
        london_time = self.downloaded_at.astimezone(pytz.timezone('Europe/London'))
        formatted_time = london_time.strftime("%b %d %Y, %I:%M %p")
        
        return {
            "id": self.id,
            "user": self.user.username,
            "format": self.format,
            "link": self.link,
            "timestamp": formatted_time,
            "filename": self.filename 
        }


    

