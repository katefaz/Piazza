from django.contrib import admin
from .models import Message, Comment, Topic, Reaction

#admin.site.register(Message)
admin.site.register(Topic)
admin.site.register(Reaction)
admin.site.register(Comment)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    class IsActive(admin.SimpleListFilter):
        title = 'is_active'
        parameter_name = 'is_active'

        def lookups(self, request, model_admin):
            return (
                ('Yes', 'Yes'),
                ('No', 'No'),
            )

        def queryset(self, request, queryset):
            value = self.value()
            if value == 'Yes':
                return queryset.filter(message_status=True)
            elif value == 'No':
                return queryset.exclude(message_status=False)
            return queryset

    list_display = ('message_heading', 'message_body', 'user', 'message_create_dt', \
        'message_status')
    list_filter = (IsActive, 'message_create_dt', 'user')
    search_fields = ('message_heading', 'message_body')
    date_hierarchy = 'message_create_dt'
    ordering = ['message_create_dt']

