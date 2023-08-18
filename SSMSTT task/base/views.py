from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Task, Comment
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from .forms import Createtask
from .models import Notification
from django.views import View
from taggit.forms import TagField
from dateutil import parser

from django.shortcuts import render
from .models import Notification


def notification_detail(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.is_read = True
    notification.save()
    return render(request, 'base/notification_detail.html', {'notification': notification})


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class NotificationList(ListView):
    model = Notification
    context_object_name = 'notifications'
    template_name = 'base/notification_list.html'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'base/task_list.html'

    def get_queryset(self):
        # Get the assignee, status, and search-area parameters from the request's GET parameters
        assignee = self.request.GET.get('assignee')
        status = self.request.GET.get('status')
        search_input = self.request.GET.get('search-area')

        # Parse the input due_date parameter into the correct format
        due_date_param = self.request.GET.get('due_date')
        try:
            due_date = parser.parse(due_date_param).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # Handle invalid input or None gracefully
            due_date = None

        # Build the queryset based on the provided parameters
        tasks = Task.objects.filter(assignees__username=self.request.user.username)

        if assignee:
            tasks = tasks.filter(assignees__username=assignee)

        if status:
            tasks = tasks.filter(status=status)

        if search_input:
            tasks = tasks.filter(title__icontains=search_input)

        if due_date:
            tasks = tasks.filter(due_date=due_date)

        return tasks.order_by('priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = context['tasks'].filter(Q(status='Not Started') | Q(status='In Progress')).count()
        context['search_input'] = self.request.GET.get('search-area', '')

        context['unique_due_dates'] = Task.objects.values_list('due_date', flat=True).distinct()
        context['unique_assignees'] = Task.objects.values_list('assignees__username', flat=True).distinct()
        context['unique_statuses'] = Task.objects.values_list('status', flat=True).distinct()

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(task=self.object)
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        comment_text = request.POST.get('comment_text')
        if comment_text:
            Comment.objects.create(user=request.user, task=task, comment_text=comment_text)
            # Create a notification for the task assignees
            for assignee in task.assignees.all():
                if assignee != request.user:
                    message = f'New comment on task: "{task.title}"'
                    Notification.objects.create(user=assignee, task=task, message=message)
        return redirect('task-detail', pk=task.pk)


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = Createtask
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = Createtask
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
