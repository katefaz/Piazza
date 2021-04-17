from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.fields import CurrentUserDefault
import datetime

#class MessageManager(models.Manager):
#    """QuerySet manager needed to handle properties"""

#    def get_queryset(self):
#        """Overrides the models.Manager method"""
#        qs = super(MessageManager, self).get_queryset()
#        return qs

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
    comment_id = models.AutoField(primary_key = True)
    comment_create_dt = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE, related_name = 'comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_made')

    class Meta:
        ordering = ('-comment_create_dt',)

    def __str__(self):
        return self.comment

    def save(self, *args, **kwargs):
        # don't save if the message has expired already
        if self.message_id.message_status == False:
            return
        else:
            super().save(*args, **kwargs)
    

class Topic(models.Model):
    choices = ['Tech', 'Politics', 'Health', 'Sport'] 
    topic_name = models.CharField(choices, max_length = 8, editable=True)
    message_id = models.ManyToManyField('Message', related_name = 'message_topics', blank=True)
    def __str__(self):
        return self.topic_name


class Reaction(models.Model):
    choices = ['Like', 'Dislike'] 
    reaction = models.CharField(choices, max_length = 7, blank=True, editable=True)
    message_id = models.ForeignKey(Message, on_delete=models.CASCADE, related_name = 'reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions_made')

    
    def save(self, *args, **kwargs):
        # don't save if the message has expired already
        if self.message_id.message_status == False:
            return
        else:
            super().save(*args, **kwargs)
    
    def __str__(self):
        return self.reaction
        
    class Meta:
        unique_together = ('message_id', 'user')
