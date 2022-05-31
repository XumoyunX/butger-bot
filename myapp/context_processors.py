from django.core.handlers.wsgi import WSGIRequest
from .models import UsersType

import json
from django.shortcuts import redirect
def check_admin(request:WSGIRequest):
    if request.user:
        user = request.user
        if user is not None and  not user.is_anonymous:
            data = UsersType.objects.filter(user=user)
            if data:
                access = data.first().accesses
                ctx = {
                    "access_types":access
                }
                return ctx
        return {}
    return {}