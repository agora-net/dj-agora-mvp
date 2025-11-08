import unicodedata

import nh3
from django import forms
from django.core import validators
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from agora.apps.core.models import UserProfile, UserProfileLink
from agora.selectors import generate_unique_handle
from agora.validators import validate_handle_available, validate_no_whitespace


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


class EditProfileForm(forms.Form):
    """Form for a user to manage their profile attributes."""

    handle = forms.CharField(
        label="Handle",
        min_length=1,
        max_length=32,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "required": False}),
        validators=[
            validators.ProhibitNullCharactersValidator,
            validate_no_whitespace,
            validators.RegexValidator(
                r"^[a-zA-Z0-9-]+$",
                message=_("Handle must contain only letters, numbers, and hyphens."),
            ),
            validate_handle_available,  # Computationally heavy so run last
        ],
    )

    job_title = forms.CharField(
        label="Job Title",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "e.g., Software Engineer",
            }
        ),
    )

    company = forms.CharField(
        label="Company",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "input input-bordered w-full", "placeholder": "e.g., Acme Corp"}
        ),
    )

    bio = forms.CharField(
        label="Bio",
        max_length=500,
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "textarea textarea-bordered w-full",
                "placeholder": "Tell us about yourself",
                "rows": 4,
            }
        ),
    )

    pronouns = forms.CharField(
        label="Pronouns",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "input input-bordered w-full", "placeholder": "e.g., they/them"}
        ),
    )

    interests = forms.CharField(
        label="Interests",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "e.g., coding, music, photography",
            }
        ),
        help_text="Enter comma-separated interests or tags",
    )

    relationship_status = forms.ChoiceField(
        label="Relationship Status",
        choices=[("", "-- Select --")] + list(UserProfile.RelationshipStatus.choices),
        required=False,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get("handle"):
            self.initial["handle"] = generate_unique_handle()
        self.fields["handle"].initial = self.initial.get("handle")

    def clean_handle(self):
        """Validate the handle."""
        raw_handle = self.cleaned_data.get("handle", "")
        handle = unicodedata.normalize("NFKC", raw_handle).strip()

        try:
            handle.encode("ascii")
        except UnicodeEncodeError:
            raise forms.ValidationError(_("Use only ASCII characters.")) from None

        handle = nh3.clean(handle)
        return handle

    def clean_bio(self):
        """Validate and sanitize bio."""
        bio = self.cleaned_data.get("bio", "")
        if bio:
            bio = nh3.clean(bio.strip())
        return bio

    def clean_interests(self):
        """Parse interests from comma-separated string to list."""
        interests_str = self.cleaned_data.get("interests", "")
        if not interests_str:
            return []

        # Split by comma and clean each interest
        interests = [nh3.clean(interest.strip()) for interest in interests_str.split(",")]
        # Filter out empty strings
        interests = [interest for interest in interests if interest]
        return interests

    def clean_pronouns(self):
        """Validate and sanitize pronouns."""
        pronouns = self.cleaned_data.get("pronouns", "")
        if pronouns:
            pronouns = nh3.clean(pronouns.strip())
        return pronouns

    def clean_job_title(self):
        """Validate and sanitize job title."""
        job_title = self.cleaned_data.get("job_title", "")
        if job_title:
            job_title = nh3.clean(job_title.strip())
        return job_title

    def clean_company(self):
        """Validate and sanitize company."""
        company = self.cleaned_data.get("company", "")
        if company:
            company = nh3.clean(company.strip())
        return company


class DonationForm(forms.Form):
    """Form for collecting donation information."""

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
        help_text="We'll send you your signup link and a receipt for your donation.",
    )

    amount_cents = forms.IntegerField(
        label="Donation amount (Swiss Francs)",
        min_value=1000,
        widget=forms.NumberInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Enter donation amount (minimum 10.00 CHF)",
                "required": True,
                "min": "1000",
            }
        ),
        help_text="Minimum donation is 10.00 CHF.",
        error_messages={
            "invalid": "Enter a valid number.",
            "min_value": "Minimum donation amount is 10.00 CHF.",
        },
    )

    def clean_email(self):
        """Validate and normalize the email address."""
        email = self.cleaned_data.get("email")
        if email:
            email = nh3.clean(email.lower().strip())
        return email

    def clean_amount_cents(self):
        """Validate the donation amount."""
        amount_cents = self.cleaned_data.get("amount_cents")
        if amount_cents and amount_cents < 1000:
            raise forms.ValidationError("Minimum donation amount is 10.00 CHF.")
        return amount_cents


# Formset for managing user profile links
UserProfileLinkFormSet = inlineformset_factory(
    UserProfile,
    UserProfileLink,
    fields=("position", "label", "url"),
    extra=1,
    can_delete=True,
)
