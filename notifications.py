from plyer import notification


def notify(title, message):
    notification.notify(title=title, message=message, timeout=5)
