from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Task, Notification


@receiver(pre_save, sender=Task)
def task_due_date_notification(sender, instance, **kwargs):
    current_date = timezone.now().date()  # Get the current date

    if instance.due_date and instance.due_date.date() <= current_date and instance.status != 'Completed':
        message = f'The task "{instance.title}" is overdue. Please complete it as soon as possible.'
        notification = Notification.objects.create(user=instance.user, task=instance, message=message)

    elif instance.due_date and (instance.due_date.date() - current_date).days <= 1 and instance.status != 'Completed':
        message = f'The task "{instance.title}" is approaching its due date. Please complete it soon.'
        notification = Notification.objects.create(user=instance.user, task=instance, message=message)
