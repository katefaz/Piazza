import django_filters.rest_framework
from rest_framework import viewsets
from rest_framework import generics, mixins
from rest_framework import permissions
from .models import Message, Comment, Topic, Reaction
from .serializers import MessageSerializer, CommentSerializer, TopicSerializer, ReactionSerializer
from .permissions import IsOwner, IsNotMessageOwner
from .filters import MessageFilter
from django.shortcuts import render
from django.views import generic
from django.db.models import F, Q, ExpressionWrapper, DurationField, Count
import datetime

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAdminUser]

class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class MessageList(generics.ListCreateAPIView):
    # view for browsing all messages
    # includes custom filter to add functionality for filtering by topic
    # and by expired vs not expired messages
    queryset = Message.objects.all().annotate(
        num_reactions = Count('reactions'),
        num_likes = Count('reactions', filter=Q(reactions__reaction='Like')), \
        num_dislikes = Count('reactions', filter=Q(reactions__reaction='Dislike')))

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = MessageFilter

class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class ReactionList(generics.ListCreateAPIView):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotMessageOwner]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

#class IndexView(generic.ListView):
#    template_name = 'piazza/index.html'
#    context_object_name = 'latest_message_list'
#    def get_queryset(self):
#        return Message.objects.order_by('-message_create_dt')