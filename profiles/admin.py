from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import TrackTrainsUser

# >>> Forms here <<< #
class TrackTrainsUserCreationForm(forms.ModelForm):
    """
    A form for creating new users.
    """
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput())
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput())

    class Meta:
        model = TrackTrainsUser
        fields = (
            "email",
            "inviter",
            "invites_counter"
        )

    def clean_password2(self):
        """
        Check that the password and password confirmation are identical.
        """
        cdata = self.cleaned_data
        password1 = cdata.get("password1")
        password2 = cdata.get("password2")
        # TODO make sure that empty check is realy necessary
        if not password1 or not password2 or not len(password1) or not len(password2):
            msg = "Both password and password confirmation must be filled"
            raise forms.ValidationError(msg)

        if password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)

        return password2

    def save(self, commit=True):
        """
        Save password in hashed format
        """
        user = super(TrackTrainsUserCreationForm, self).save(commit=False)
        cdata = self.cleaned_data
        user.set_password(cdata['password2'])
        if commit:
            user.save()
        return user

class TrackTrainsUserChangeForm(forms.ModelForm):
    """
    Form for updating users
    Replaces the password field changed to hashed password
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = TrackTrainsUser
        fields = '__all__'

    def clean_password(self):
        """
        Password can't be changed, returns the initial password
        """
        return self.initial["password"]

# >>> Admin model here <<< #

class TrackTrainsUserAdmin(UserAdmin):
    add_form = TrackTrainsUserCreationForm
    form = TrackTrainsUserChangeForm

    list_display = (
        "email",
        "is_staff",
        "inviter",
        "invites_counter"
    )

    list_filter = (
        "is_superuser",
        "is_staff",
        "is_active",
        "groups"
    )

    search_fields = (
        "email",
        "inviter"
    )

    ordering = ("email",)

    filter_horizontal = ("groups", "user_permissions", )

    exclude = ('reset_hash', )

    fieldsets = (
        (None, {"fields": (
            "email",
            "password"
        )}),
        ("Personal Info", {"fields": (
            "inviter",
            "invites_counter"
        )}),
        ("Permissions", {"fields": (
            "is_superuser",
            "is_staff",
            "groups",
            "user_permissions"
        )}),
        ("Dates", {"fields": ("last_login",)})
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "inviter",
                "invites_counter",
                "password1",
                "password2"
            )}
        ),
    )

# >>> Registers admin models here <<< #
admin.site.register(
    TrackTrainsUser,
    TrackTrainsUserAdmin)
