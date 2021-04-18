from rest_framework import serializers
from .models import Message, Comment, Topic, Reaction
from django.db.models import F

class CommentSerializer(serializers.ModelSerializer):
    '''
    Supports commenting on related messages
    '''
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Comment
        fields = ('comment_id', 'comment_create_dt', \
             'comment', 'user' , 'message_id'
                )
    def save(self, **kwargs):
        ''' overwrite save to manage user and message_id foreign keys'''
        kwargs['user'] = self.fields['user'].get_default()
        return super().save(**kwargs)

class TopicSerializer(serializers.ModelSerializer):
    '''
    Supports viewing topics and related messages
    '''
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Topic
        fields = ('id', 'topic_name','messages')

class ReactionSerializer(serializers.ModelSerializer):
    '''
    Supports liking / disliking a message
    '''
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Reaction
        fields = ('id', 'user', 'message_id','reaction')

    def validate(self, data):
        """
        Check that reaction is to a user's own message 
        """ 
        message = Message.objects.get(pk=data['message_id'].message_id)
        
        if message.user_id == self.fields['user'].get_default().id:
            raise serializers.ValidationError('Reaction must not be to a users own message.')

        return data

    def save(self, **kwargs):
        ''' overwrite save to manage user'''
        kwargs['user'] = self.fields['user'].get_default()
        return super().save(**kwargs)

class MessageSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    comments = CommentSerializer(many=True, read_only=True)
    
    num_reactions = serializers.IntegerField(read_only=True)
    num_likes = serializers.IntegerField(read_only=True)
    num_dislikes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Message
        fields = ('message_id', 'message_create_dt', \
             'message_heading', 'message_body',\
                'message_expires', 
                'user', 'comments', 'message_topics',
                'message_status', 'num_reactions', 'num_likes',
                'num_dislikes')
   
    
    def save(self, **kwargs):
        ''' overwrite save to manage user foreign key'''
        kwargs['user'] = self.fields['user'].get_default()
        return super().save(**kwargs)

