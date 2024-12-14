#from django.shortcuts import render
#from django.utils import timezone
#from .models import Post

# Create your views here.
#def post_list(request):
#    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
#    return render(request, 'blog/post_list.html', {'posts': posts})
from django.shortcuts import redirect, render 
from django.utils import timezone

from blog.forms import PostForm 
from .models import Post
from django.shortcuts import render, get_object_or_404

#added
from rest_framework import viewsets
from .serializers import PostSerializer
import firebase_admin
from firebase_admin import credentials, messaging
import os

# Firebase Admin SDK 초기화
current_dir = os.path.dirname(__file__)
target_file = os.path.join(current_dir, 'notify.json')
cred = credentials.Certificate(target_file)
firebase_admin.initialize_app(cred)

class blogImage(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    def perform_create(self, serializer):
        """포스트가 생성될 때 알림을 전송"""
        # 포스트 객체 생성
        post = serializer.save()

        # 포스트 타이틀을 알림으로 전송
        send_fcm_notification(
            title=str(post.title),
            body=str(post.title)  # 포스트 내용의 일부를 알림에 포함
        )
        

def post_list(request):
    posts = Post.objects.filter().order_by('published_date') 
    return render(request, 'blog/post_list.html', {'posts': posts})
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def send_fcm_notification(title, body):

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        topic="default_channel",  # FCM 주제, 구독한 모든 기기에게 메시지 전송
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                sound="default",  # 기본 알림 소리 설정
                click_action="FLUTTER_NOTIFICATION_CLICK",  # 알림 클릭 시 동작
            )
        )
    )

    # 메시지 전송
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print('Error sending message:', e)



def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})