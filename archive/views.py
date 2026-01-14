from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from tasks.models import Task, TaskSubmission
from minutes.models import Minutes
from django.db.models import Q


def _is_admin(user):
    return user.is_staff or user.is_superuser

def admin_required(view_func):
    return login_required(user_passes_test(_is_admin)(view_func))

@login_required
def archive_home(request):
    # Admin-only archive (مثل ما طلبتي)
    if not _is_admin(request.user):
        return HttpResponseForbidden("Admin only")

    return render(request, "archive/archive_home.html")
@login_required
def archive_solutions(request):
    """
    كل الحلول المقدّمة:
    - الحل الموجود داخل Task (solution_text/solution_file + submitted_by/submitted_at)
    - أو Submissions (TaskSubmission)
    """
    tasks_with_solution = (
        Task.objects
        .filter(Q(solution_text__gt="") | Q(solution_file__isnull=False) | Q(submitted_at__isnull=False))
        .select_related("meeting", "assigned_to", "submitted_by")
        .order_by("-submitted_at", "-created_at")
    )

    submissions = (
        TaskSubmission.objects
        .select_related("task", "submitted_by", "task__meeting")
        .order_by("-submitted_at")
    )

    return render(request, "archive/solutions.html", {
        "tasks_with_solution": tasks_with_solution,
        "submissions": submissions,
    })


@login_required
def archive_minutes(request):
    """
    محاضر الاجتماعات + (قرارات إن كانت موجودة داخل نفس موديل Minutes عندك)
    """
    minutes_list = (
        Minutes.objects
        .select_related("meeting")
        .order_by("-created_at")
    )
    return render(request, "archive/minutes.html", {"minutes_list": minutes_list})


@login_required
def archive_attachments(request):
    """
    نجمع كل الملفات المتاحة الآن:
    - Task.solution_file
    - TaskSubmission.file
    (وبعدين نضيف تسجيل الاجتماع لما تجهزين Model/تكامل Jitsi)
    """
    task_files = (
        Task.objects
        .filter(solution_file__isnull=False)
        .exclude(solution_file="")
        .select_related("meeting", "submitted_by")
        .order_by("-submitted_at", "-created_at")
    )

    submission_files = (
        TaskSubmission.objects
        .filter(file__isnull=False)
        .exclude(file="")
        .select_related("task", "submitted_by", "task__meeting")
        .order_by("-submitted_at")
    )

    return render(request, "archive/attachments.html", {
        "task_files": task_files,
        "submission_files": submission_files,
    })