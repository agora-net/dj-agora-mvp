import nh3
from django import forms


class WaitlistSignupForm(forms.Form):
    """Form for signing up to the waitlist with email address."""

    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Enter your email address",
                "required": True,
            }
        ),
        help_text="We'll notify you when Agora is ready for you to use.",
    )

    def clean_email(self):
        """Validate and normalize the email address."""
        email = self.cleaned_data.get("email")
        if email:
            email = nh3.clean(email.lower().strip())
        return email


class AcceptInviteForm(forms.Form):
    """Form for accepting an invite."""

    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "input input-bordered w-full",
                "required": True,
                "disabled": True,
                "readonly": True,
            }
        ),
    )
    invite_code = forms.CharField(
        label="Invite code",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "required": True,
                "disabled": True,
                "hidden": True,
            }
        ),
    )
    name = forms.CharField(
        label="Name",
        max_length=512,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "required": True}),
    )
    handle = forms.CharField(
        label="Handle",
        max_length=32,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "required": False}),
    )

    def clean(self):
        """Clean the form data by sanitizing the string values using nh3."""
        cleaned_data = super().clean()
        for field in self.fields:
            value = cleaned_data.get(field)
            if isinstance(value, str):
                cleaned_data[field] = nh3.clean(value)
        return cleaned_data
