Loaded Config
{'communities': {'init_with': [{'auto_populate_with_test_data': True,
                                'id': 'uwe',
                                'name': 'UWE',
                                'owner_username': 'admin'},
                               {'auto_populate_with_test_data': True,
                                'id': 'comp-sci',
                                'name': 'Computer Science',
                                'owner_username': 'admin'}]},
 'email_domain': 'live.uwe.ac.uk',
 'name': 'UWEHub',
 'users': {'init_with': [{'email': 'unihub@',
                          'first_name': 'UWE',
                          'is_staff': True,
                          'is_superuser': True,
                          'last_name': 'Hub',
                          'password': 'password',
                          'profile_picture': '',
                          'student_id': 0,
                          'username': 'admin'}]}}
admin
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountsCourse(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'accounts_course'


class AccountsCustomuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    bio = models.TextField()
    profile_picture = models.CharField(max_length=100, blank=True, null=True)
    course = models.ForeignKey(AccountsCourse, models.DO_NOTHING, blank=True, null=True)
    student_id = models.CharField(unique=True, max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accounts_customuser'


class AccountsCustomuserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_customuser_groups'
        unique_together = (('customuser', 'group'),)


class AccountsCustomuserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class AccountsFollow(models.Model):
    id = models.BigAutoField(primary_key=True)
    followee = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    follower = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING, related_name='accountsfollow_follower_set')

    class Meta:
        managed = False
        db_table = 'accounts_follow'
        unique_together = (('follower', 'followee'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class CommunitiesCommunities(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)
    pkid = models.BigAutoField(primary_key=True)
    id = models.CharField(unique=True, max_length=25)
    name = models.CharField(max_length=255)
    description = models.TextField()
    banner_url = models.CharField(max_length=200, blank=True, null=True)
    icon_url = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    owner = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'communities_communities'


class CommunitiesCommunitiesTopics(models.Model):
    id = models.BigAutoField(primary_key=True)
    communities = models.ForeignKey(CommunitiesCommunities, models.DO_NOTHING)
    topic = models.ForeignKey('CommunitiesTopic', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'communities_communities_topics'
        unique_together = (('communities', 'topic'),)


class CommunitiesCommunitymember(models.Model):
    id = models.BigAutoField(primary_key=True)
    joined_at = models.DateTimeField()
    role = models.CharField(max_length=20)
    community = models.ForeignKey(CommunitiesCommunities, models.DO_NOTHING)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'communities_communitymember'
        unique_together = (('user', 'community'),)


class CommunitiesTopic(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'communities_topic'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class PostsInteraction(models.Model):
    id = models.BigAutoField(primary_key=True)
    interaction = models.CharField(max_length=20)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)
    post = models.ForeignKey('PostsPost', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'posts_interaction'


class PostsPost(models.Model):
    pkid = models.BigAutoField(primary_key=True)
    id = models.CharField(unique=True)
    title = models.CharField(max_length=60)
    body = models.TextField()
    is_pinned = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    community = models.ForeignKey(CommunitiesCommunities, models.DO_NOTHING, blank=True, null=True)
    parent_post = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    ref_post = models.ForeignKey('self', models.DO_NOTHING, related_name='postspost_ref_post_set', blank=True, null=True)
    user = models.ForeignKey(AccountsCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'posts_post'
