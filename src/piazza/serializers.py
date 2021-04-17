from rest_framework import serializers
from .models import Message, Comment, Topic, Reaction
from django.db.models import F

class CommentSerializer(serializers.ModelSerializer):
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
    # support viewing topics and related messages
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Topic
        fields = ('id', 'topic_name','messages')

class ReactionSerializer(serializers.ModelSerializer):
    # supports liking / disliking a message
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Reaction
        fields = ('id', 'user', 'message_id','reaction')

    def validate_user(self, value):
        """
        Check that user is not reacting to their own message
        """
        if value == Message.objects.all().Filter(message_id= self.initial_data['message_id'])[0].user_id:
            raise serializers.ValidationError("User cannot react to own message")
        
        return value

    def validate_reaction(self, value):
        """
        Check that reaction is either Like or Dislike
        """
        if (value not in ['Like', 'Dislike']) and value:
            raise serializers.ValidationError("Reaction must be either Like or Dislike")
        return value

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


