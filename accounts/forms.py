from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


# -------------------------
# Basic Forms (existing)
# -------------------------
class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["face_image"]
        widgets = {
            "face_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


# -------------------------
# Admin HR Panel Forms (WARF)
# -------------------------
class EmployeeCreateForm(forms.ModelForm):
    """
    Admin creates a new employee:
    - username, email, first_name, last_name
    - password (set once)
    - profile fields: status, face_image
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        min_length=6,
        help_text="Set a temporary password for the employee."
    )

    status = forms.ChoiceField(
        choices=Profile.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        initial="active"
    )

    face_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already used.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_staff = False
        user.is_superuser = False

        if commit:
            user.save()

            # profile auto-created by signal
            profile = user.profile
            profile.status = self.cleaned_data["status"]
            if self.cleaned_data.get("face_image"):
                profile.face_image = self.cleaned_data["face_image"]
            profile.save()

        return user


class EmployeeUpdateForm(forms.ModelForm):
    """
    Admin edits an existing employee + profile.
    Password is optional (reset).
    """
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Leave empty to keep the current password."
    )

    status = forms.ChoiceField(
        choices=Profile.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    face_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile")
        super().__init__(*args, **kwargs)
        self.fields["status"].initial = self.profile.status

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if email and qs.exists():
            raise forms.ValidationError("This email is already used.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        # optional password reset
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)

        if commit:
            user.save()

            self.profile.status = self.cleaned_data["status"]
            if self.cleaned_data.get("face_image"):
                self.profile.face_image = self.cleaned_data["face_image"]
            self.profile.save()

        return user
