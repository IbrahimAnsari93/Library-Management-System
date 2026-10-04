from .models import Notification


def notifications_context(request):
    if not request.user.is_authenticated:
        return {
            "navbar_notifications": [],
            "navbar_unread_count": 0,
        }

    if not request.user.is_staff:
        return {
            "navbar_notifications": [],
            "navbar_unread_count": 0,
        }

    from .views import generate_notifications

    generate_notifications()

    unread_count = Notification.objects.filter(
        is_read=False
    ).count()

    latest_notifications = Notification.objects.all().order_by(
        "-created_at"
    )[:5]

    return {
        "navbar_notifications": latest_notifications,
        "navbar_unread_count": unread_count,
    }
