from django import forms
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()

class TaskAssignForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["assigned_to", "due_date", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # شكل Bootstrap
        for f in self.fields.values():
            f.widget.attrs.update({"class": "form-control form-control-sm"})

        # نجبر status يكون assigned/done فقط من صفحة الأدمن
        self.fields["status"].choices = [
            ("todo", "To Do"),
            ("assigned", "Assigned"),
            ("done", "Done"),
        ]

        # قائمة الموظفين (غير السوبر يوزر)
        self.fields["assigned_to"].queryset = User.objects.filter(is_superuser=False).order_by("username")
        self.fields["assigned_to"].required = False
