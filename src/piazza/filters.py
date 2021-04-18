import django_filters
from .models import Message, Comment, Topic 
from django.db.models import F, ExpressionWrapper, DurationField, Max, Count
import datetime

class MessageFilter(django_filters.FilterSet):
    message_topic = django_filters.filters.ModelMultipleChoiceFilter(
        field_name='message_topics',
        to_field_name='id',
        queryset=Topic.objects.all()
        )

    message_most_reactions = django_filters.filters.BooleanFilter(method = 'filter_message_most_reactions')

    def filter_message_most_reactions(self, queryset, name, value):
        if value==True:
            max_reactions = list(queryset.aggregate(Max(Count('reactions'))).values())[0]
            queryset = queryset.annotate(num_reactions = Count('reactions')).filter(num_reactions=max_reactions)
        else:
            queryset = queryset
        return queryset

    message_active = django_filters.filters.BooleanFilter(method = 'filter_message_active')

    def filter_message_active(self, queryset, name, value):
        if value==True:
            queryset = queryset.filter(message_expires__gte=datetime.datetime.now().astimezone())
        elif value==False:
            queryset = queryset.filter(message_expires__lt=datetime.datetime.now().astimezone())
        else:
            queryset = queryset
        return queryset
    
    class Meta:
        model = Message
        fields = ('message_topic', 'message_active', 'message_most_reactions')
