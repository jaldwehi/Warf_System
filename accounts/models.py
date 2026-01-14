from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Custom User model for WARF.
    Extended later if needed.
    """
    pass


class Profile(models.Model):
    """
    Administrative profile for each employee.
    """
    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("left", "Left"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    face_image = models.ImageField(
        upload_to="faces/reference/",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.status})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_user(sender, instance, created, **kwargs):
    """
    Automatically create a Profile for each new User.
    """
    if created:
        Profile.objects.create(user=instance)
