from .models import Notification
from accounts.models import CustomUser
from posts.models import Post
from django.urls import reverse
from accounts.models import UserSettings

class NotificationManager:
    @staticmethod
    def send_follow(username,follower_username):
        user = CustomUser.objects.get(username=username)
        user_settings = UserSettings.objects.get(user_id=user.id)
        if user_settings.follow_notifications: 
            follower = CustomUser.objects.get(username=follower_username)
            profile_link = reverse('user', kwargs={'username': follower})
            notification = Notification.objects.create(
                username=user,
                type='follow',
                data={'sender': follower.username,
                    'profile_link':profile_link,
                    }
                )
            return notification
        pass
    
    @staticmethod 
    def send_like(username,liker_username, post_id):
        user = CustomUser.objects.get(username=username)
        user_settings = UserSettings.objects.get(user_id=user.id)
        if user_settings.like_notifications:
            liker = CustomUser.objects.get(username=liker_username)
            post = Post.objects.get(id=post_id)
            post_link = reverse('post', kwargs={'post_id':post.id})
            notification = Notification.objects.create(
                username=user,
                type='like',
                data={'sender':liker.username
                    ,'post_link': post_link
                    }
            )
            return notification
        pass
    
    @staticmethod 
    def send_comment(username,commenter_username, post_id):
        user = CustomUser.objects.get(username=username)
        user_settings = UserSettings.objects.get(user_id=user.id)
        if user_settings.comment_notifications: 
            commenter = CustomUser.objects.get(username=commenter_username)
            post = Post.objects.get(id=post_id)
            post_link = reverse('post', kwargs={'post_id':post.id})
            notification = Notification.objects.create(
                username=user,
                type='comment',
                data={'sender':commenter.username
                    ,'post_link': post_link
                    }
            )
            return notification
        pass

    @staticmethod
    def send_community_request(superuser, community):
        notification = Notification.objects.create(
            username=superuser,
            type='community_request',
            data={
                'community_id': community.id,
                'community_name': community.name,
                'sender': community.owner.username
            }
        )
        return notification

    @staticmethod
    def send_role_request(owner, community, requester, role):
        notification = Notification.objects.create(
            username=owner,
            type='role_request',
            data={
                'community_id': community.id,
                'community_name': community.name,
                'requested_role': role,
                'sender': requester.username
            }
        )
        return notification
    
    @staticmethod
    def role_decision(requester, community, role, decision):
        notification = Notification.objects.create(
            username=requester,
            type='role_decision',
            data={
                'community_id': community.id,
                'community_name': community.name,
                'role': role,
                'decision': decision
            }
        )
        return notification
    
    @staticmethod
    def community_decision(owner, community, decision):
        notification = Notification.objects.create(
            username=owner,
            type='community_decision',
            data={
                'community_id': community.id,
                'community_name': community.name,
                'decision': decision
            }
        )
        return notification