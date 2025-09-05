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
