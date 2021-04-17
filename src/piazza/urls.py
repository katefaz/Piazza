from django.urls import path
from . import views

urlpatterns = [
    path('message/', views.MessageList.as_view()),
    path('message/<int:pk>/', views.MessageDetail.as_view()),
    path('comment/', views.CommentList.as_view()),
    path('comment/<int:pk>/', views.CommentDetail.as_view()),
    path('reaction/', views.ReactionList.as_view())]