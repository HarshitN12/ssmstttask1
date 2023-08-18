from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager
from django.urls import reverse

STATUS_CHOICES = [
    ('Not Started', 'Not Started'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
]
PRIORITY_CHOICES = [
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
]


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True)
    assignees = models.ManyToManyField(User, default="", related_name='assigned_tasks', blank=True)
    tags = TaggableManager()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['status']


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('notification-detail', args=[str(self.id)])


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    comment_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.task.title}'
