from .models import Notification
from accounts.models import CustomUser

class NotificationManager:
    @staticmethod
    def create_follow(username,follower_username):
        user = CustomUser.objects.get(username=username)
        follower = CustomUser.objects.get(username=follower_username)
        notification = Notification.objects.create(
            username=user,
            type='follow',
            data={'follower_username': follower.username}
            )
        return notification
    
    @staticmethod 
    def create_like(username, sender_username, post_id):
        user = CustomUser.objects.get(username=username)
        sender = CustomUser.objects.get(username=sender_username)
        notification = Notification.objects.create(
            username=user,
            type='like',
            data={'sender_username':sender.username
                  #,'post_link': post_id (WIP // need to figure how the format of the url for posts)
                  }
        )