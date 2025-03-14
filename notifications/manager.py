from .models import Notification
from accounts.models import CustomUser
from posts.models import Post
from django.urls import reverse

class NotificationManager:
    @staticmethod
    def send_follow(username,follower_username):
        user = CustomUser.objects.get(username=username)
        follower = CustomUser.objects.get(username=follower_username)
        profile_link = reverse('user', kwargs={'username': follower})
        notification = Notification.objects.create(
            username=user,
            type='follow',
            data={'follower_username': follower.username,
                  'profile_link':profile_link,
                  }
            )
        return notification
    
    @staticmethod 
    def send_like(username,liker, post_id):
        user = CustomUser.objects.get(username=username)
        liker = CustomUser.objects.get(username=liker)
        post = Post.objects.get(id=post_id)
        post_link = reverse('post', kwargs={'id':post})
        notification = Notification.objects.create(
            username=user,
            type='like',
            data={'liker_username':liker.username
                  ,'post_link': post_link
                  }
        )
        return notification
    
    @staticmethod 
    def send_comment(username,commenter, post_id):
        user = CustomUser.objects.get(username=username)
        commenter = CustomUser.objects.get(username=commenter)
        post = Post.objects.get(id=post_id)
        post_link = reverse('post', kwargs={'id':post})
        notification = Notification.objects.create(
            username=user,
            type='comment',
            data={'commenter_username':user.username
                  ,'post_link': post_link
                  }
        )