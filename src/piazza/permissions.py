from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsNotMessageOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        message = Message.objects.get(pk=request.data['message_id'])
        return message.user_id != request.user
