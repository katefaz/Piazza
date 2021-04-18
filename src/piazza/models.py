from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault
import datetime

class Message(models.Model):

    message_id = models.AutoField(primary_key = True)
    message_create_dt = models.DateTimeField(auto_now_add=True)
    message_heading = models.TextField()
    message_body = models.TextField()
    message_topic = models.ManyToManyField('Topic', related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    message_expires = models.DateTimeField(default=(datetime.datetime.now().astimezone() \
         + datetime.timedelta(minutes=75)))

    @property
    def message_status(self):
        ''' Determines whether the post has expired or not'''
        return (self.message_expires - datetime.datetime.now().astimezone()) > datetime.timedelta(seconds=0)

    class Meta:
        ordering = ('-message_create_dt',)

    def __str__(self):
        return self.message_heading

class Comment(models.Model):

    def validate_message_active(value):
        """
        Check that the related message is still active
        """
        message = Message.objects.get(pk=value.message_id)
        if message.message_status == False:
            raise ValidationError("Comment must be to an active message")
        return value

    comment_id = models.AutoField(primary_key = True)
    comment_create_dt = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE, related_name = 'comments', validators = [validate_message_active])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_made')

    class Meta:
        ordering = ('-comment_create_dt',)

    def __str__(self):
        return self.comment

class Topic(models.Model):
    choices = ['Tech', 'Politics', 'Health', 'Sport'] 
    topic_name = models.CharField(choices, max_length = 8, editable=True)
    message_id = models.ManyToManyField('Message', related_name = 'message_topics', blank=True)
    def __str__(self):
        return self.topic_name


class Reaction(models.Model):
    
    def validate_reaction(value):
        """
        Check that reaction is either Like or Dislike
        """
        if (value not in ['Like', 'Dislike']) and value:
            raise ValidationError("Reaction must be either Like or Dislike")
        return value
    
    def validate_message_active(value):
        """
        Check that the related message is still active
        """
        if type(value)=='int':
            message = Message.objects.get(pk=value)
        else: 
            message = Message.objects.get(pk=int(value.message_id))
        if message.message_status == False:
            raise ValidationError("Reaction must be to an active message")
        return value

    choices = ['Like', 'Dislike'] 
    reaction = models.CharField(choices, max_length = 7, blank=True, editable=True, validators = [validate_reaction])
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE, related_name = 'reactions', validators = [validate_message_active])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions_made')

    def __str__(self):
        return self.reaction
        
    class Meta:
        unique_together = ('message_id', 'user')
