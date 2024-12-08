from api.models import ActivityLog


def raise_event(user, status, action, model_name, context='', data=None, request=None):
    ip_address = None
    if request is not None:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    ActivityLog.objects.create(
        user=user,
        status=status,
        action=action,
        model=model_name,
        context=context,
        data=data if data is not None else {},
        ip_address=ip_address
    )
