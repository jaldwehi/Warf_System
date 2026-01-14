from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import Task

User = get_user_model()


def _is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
def tasks_list(request):
    is_admin = _is_admin(request.user)

    qs = Task.objects.select_related("meeting", "assigned_to").order_by("-created_at")

    # Employee sees only their tasks
    if not is_admin:
        qs = qs.filter(assigned_to=request.user)

    # --------------------------
    # POST handlers
    # --------------------------
    if request.method == "POST":

        # ✅ Employee submits solution
        action = (request.POST.get("action") or "").strip()
        if action == "submit_solution" and not is_admin:
            task_id = request.POST.get("task_id")
            task = get_object_or_404(Task, id=task_id, assigned_to=request.user)

            solution_text = (request.POST.get("solution_text") or "").strip()
            solution_file = request.FILES.get("solution_file")

            if not solution_text and not solution_file:
                messages.error(request, "Please provide solution text or upload a file.")
                return redirect("tasks:list")

            # حفظ الحل
            task.solution_text = solution_text
            if solution_file:
                task.solution_file = solution_file

            task.submitted_at = timezone.now()
            task.submitted_by = request.user

            # منطق الحالة: أول تسليم يخليها In Progress (ونقدر نخليها Done لاحقًا بموافقة الأدمن)
            if task.status == "todo":
                task.status = "in_progress"

            task.save(update_fields=[
                "solution_text",
                "solution_file",
                "submitted_at",
                "submitted_by",
                "status",
            ])

            messages.success(request, "Solution submitted successfully.")
            return redirect("tasks:list")

        # ✅ Admin can assign/update tasks
        if is_admin:
            task_id = request.POST.get("task_id")
            assigned_to_id = request.POST.get("assigned_to")
            status = (request.POST.get("status") or "").strip()
            due_date_raw = (request.POST.get("due_date") or "").strip()

            task = get_object_or_404(Task, id=task_id)

            # assigned_to
            if assigned_to_id:
                user = User.objects.filter(id=assigned_to_id).first()
                task.assigned_to = user
            else:
                task.assigned_to = None

            # status
            allowed_status = {k for k, _ in Task.STATUS_CHOICES}
            if status in allowed_status:
                task.status = status

            # due_date
            if due_date_raw:
                task.due_date = parse_date(due_date_raw)
            else:
                task.due_date = None

            task.save(update_fields=["assigned_to", "status", "due_date"])
            messages.success(request, "Task updated.")
            return redirect("tasks:list")

    users = User.objects.all().order_by("username") if is_admin else User.objects.none()

    return render(request, "tasks/tasks_list.html", {
        "tasks": qs,
        "is_admin": is_admin,
        "users": users,
    })

