import json
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from pathlib import Path
from django.templatetags.static import static
from django.conf import settings
from pytube import YouTube
import requests
from django.http import StreamingHttpResponse
import subprocess
from .models import User, Download
import re
from django.core.mail import send_mail
from django.utils import timezone
import pytz
from datetime import datetime
from django.contrib.staticfiles.storage import staticfiles_storage
import random
from pytube.innertube import _default_clients
from pytube import cipher
from pytubefix import YouTube
from pytubefix.cli import on_progress

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    #logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            #logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise re.error(
        caller="get_throttling_function_name", pattern="multiple"
    )

cipher.get_throttling_function_name = get_throttling_function_name

# Create your views here.
def index(request):
    
    newImageUrl = newImageUrl_()
    link = request.GET.get('link', '')
    format = request.GET.get('format', '')


    if request.user.is_authenticated:
        return render(request, "web/index.html", {"user": request.user, "newImageUrl": newImageUrl, "link": link, "format": format})
    else:
        return render(request, "web/login.html", {"user": request.user, "newImageUrl": newImageUrl})




@login_required
def download(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        # Validate and extract the YouTube link
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+/|watch\?v=|watch/|shorts/)?'
            r'([^&=%\?]{11})(\S*)'
        )
        data = json.loads(request.body)
        format = data["format"]
        link = data["link"]

        if not youtube_regex.match(link):
            return JsonResponse({"error": "Invalid link"}, status=400)

        try:
            # Initialize YouTube object with the provided link
            yt = YouTube(link, on_progress_callback = on_progress)
        except Exception as e:
            return JsonResponse({"error": f"Failed to initialize YouTube object: {e}"}, status=500)

        try:
            # Get the highest resolution stream available
            video = yt.streams.get_highest_resolution()
        except Exception as e:
            return JsonResponse({"error": f"Failed to get video stream: {e}"}, status=500)

        # Define a generator function to stream the video content
        def stream_video():
            try:
                response = requests.get(video.url, stream=True)
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    yield chunk
            except requests.RequestException as e:
                raise Exception(f"Failed to stream video content: {e}")

        try:
            if format == "mp4":
                response = StreamingHttpResponse(stream_video(), content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="{yt.title}.mp4"'
                response['Content-Length'] = requests.head(video.url).headers.get('Content-Length', None)
                response["X-Filename"] = f"{yt.title}.mp4"
                return response

            elif format == "mp3":
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-i", "pipe:0",       # Read from stdin
                    "-vn",                # Disable video recording
                    "-acodec", "libmp3lame",
                    "-ab", "192k",        # Audio bitrate
                    "-ar", "44100",       # Audio sampling rate
                    "-f", "mp3",          # Force MP3 format
                    "pipe:1"              # Write to stdout
                ]

                # Start FFmpeg subprocess with stdin=subprocess.PIPE to accept input
                ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                
                # Feed video chunks to FFmpeg stdin and get MP3 data
                mp3_data, _ = ffmpeg_process.communicate(input=b''.join(stream_video()))
                # Create a streaming response for the MP3 data
                response = StreamingHttpResponse(iter([mp3_data]), content_type='audio/mpeg')
                response['Content-Disposition'] = f'attachment; filename="{yt.title}.mp3"'
                response['Content-Length'] = len(mp3_data)
                response["X-Filename"] = f"{yt.title}.mp3"
                return response
            else:
                return JsonResponse({"error": "Invalid Format"}, status=400)

        except subprocess.SubprocessError as e:
            return JsonResponse({"error": f"FFmpeg error: {e}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": f"Failed to process video: {e}"}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON input"}, status=400)
    except KeyError as e:
        return JsonResponse({"error": f"Missing parameter: {e}"}, status=400)
    except Exception as e:
        # Handle any other exceptions that occur during the process
        print(f"Error: {e}")
        return HttpResponse(f"Failed to download video: {e}", status=500)
    
    
@csrf_exempt
def landing_page(request):
    # Extract the parameters from the GET request
    format = request.GET.get('format')
    link = request.GET.get('link')
    return render(request, 'landing_page.html', {'format': format, 'link': link})
    
@login_required
@csrf_exempt
def history(request,user=None):
    if request.method == "POST":
        data = json.loads(request.body)
        downaload = Download.objects.create(user=request.user,format=data.get("format"), link=data.get("link"), filename=data.get("filename"))
        downaload.save()
        return JsonResponse({"message": "Post uploaded successfully."}, status=201)
    
    if request.method == "GET":
        user = User.objects.get(username=user)
        return JsonResponse({'downloads': [i.serialize() for i in user.downloads.all()]})

@login_required
@csrf_exempt
def history_view(request):
    
    return render(request, "web/history.html", {
                  "newImageUrl": newImageUrl_()
                })
    
@login_required
@csrf_exempt    
def send_email_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filename= data.get("filename")
            
            base_url = request.build_absolute_uri(reverse('index'))
            link = data.get("link")
            format = data.get("format")

            button_url = f"{base_url}?link={link}&format={format}"
            html_message = f"""
                <html>
                    <body>
                        <p>Your download was successful! Click below to download it again.</p>
                        <h1>{filename}</h1>
                        <a href="{button_url}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; text-align: center; text-decoration: none; border-radius: 5px;">Download</a>
                    </body>
                </html>
            """
            
            send_mail(
                "New Download",
                "",
                "settings.EMAIL_HOST_USER",
                [request.user.email],
                fail_silently=False,
                html_message=html_message
            )
            return JsonResponse({"message": "Email sent successfully."}, status=201)
        except Exception as e:
            return JsonResponse({"error": e}, status=500)
    return JsonResponse({"error": "It must be a POST request"}, status=500)
         
    
@login_required
@csrf_exempt
def history_view_pages(request):
  
    
    downloads = User.objects.get(username=request.user).downloads.all()
    downloads = downloads.order_by("-downloaded_at").all()
    p= Paginator(downloads,10)
    pages= []
    for i in range(1,p.num_pages+1):
        page = {"page": i, "next": p.page(i).has_next(), "previous":p.page(i).has_previous(), "downloads": [download.serialize() for download in p.page(i).object_list]}
        pages.append(page)
    return JsonResponse({"pages":pages}, safe=False)
    
    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "web/login.html", {
                "message": "Invalid username and/or password.",
                "newImageUrl": newImageUrl_()
            })
    else:
        return render(request, "web/login.html")
        
def contact_us(request):
    return render(request, "web/contact_us.html", {
                  "newImageUrl": newImageUrl_(), "email": request.user.email, 
                  "name": request.user
                })
    
def contact_form(request):
    name = request.user
    email = request.user.email
    subject = request.POST["subject"]
    message = request.POST["message"]
    
    try:
        
        
        send_mail(
                f"New Contact Request: {subject} ",
                message,
                "settings.EMAIL_HOST_USER",
                ["wecrafttechandfinance@gmail.com"],
                fail_silently=False,
            )
    
        send_mail(
            f"We received your contact request: {subject} ",
            f"Hi, {name}. We will respond you as soon as possible. Thanks for your patience",
            "settings.EMAIL_HOST_USER",
            [email],
            fail_silently=False,
        )
        
        return JsonResponse({"message":"Your message was sent"}, safe=False)
    
    except: 
        return JsonResponse({"error":"Try again or later"}, safe=False)
        
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def newImageUrl_():
   
    image_files = []
    # Path to the Background folder
    background_folder = os.path.join(settings.STATIC_ROOT, 'web', 'Background')

    # Check if the folder exists
    if os.path.exists(background_folder):
        # List only files in the Background folder
        l= os.listdir(background_folder)
        for filename in l:
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')):
                # Construct the full file path
                file_path = os.path.join(background_folder, filename)
                # Create a URL to the file
                image_url = f'web/Background/{filename}'
                image_files.append(image_url)

        # We choose a random image and return it
        
        return staticfiles_storage.url(random.choice(image_files))

    
        
    else:
        print(f"The directory {background_folder} does not exist.")
        return staticfiles_storage.url('web/Background/poderosa-galaxia_2880x1800_xtrafondos.com.jpg')
  

    
    
   
    