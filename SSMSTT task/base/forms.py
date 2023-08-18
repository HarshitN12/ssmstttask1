from django import forms
from .models import Task
from django.contrib.auth.models import User


class Createtask(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'due_date', 'assignees', 'tags', 'priority']

    assignees = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)
