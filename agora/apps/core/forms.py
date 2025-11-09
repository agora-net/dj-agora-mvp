import unicodedata
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlparse, urlunparse

import nh3
from django import forms
from django.core import validators
from django.forms import BaseInlineFormSet, inlineformset_factory
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
            # validate_handle_available is called in clean_handle with user context
        ],
    )

    job_title = forms.CharField(
        label="Job Title",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Researcher, Engineer, etc.",
            }
        ),
    )

    company = forms.CharField(
        label="Company",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "input input-bordered w-full", "placeholder": "Acme Corp"}
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
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "They/Them, He/Him, She/Her ...",
            }
        ),
    )

    interests = forms.CharField(
        label="Interests",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "coding, music, photography",
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

    is_public = forms.BooleanField(
        label="Make profile public",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "toggle toggle-primary"}),
        help_text=(
            "If checked, your profile will be visible to everyone, including unauthenticated users."
        ),
    )

    profile_image = forms.ImageField(
        label="Profile Image",
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*", "class": "hidden"}),
        help_text="Upload a profile picture (JPEG, PNG, WebP, HEIC, JPEGXL, JPEG2000). Max 5MB.",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
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

        # Validate handle availability, excluding current user if provided
        validate_handle_available(handle, user=self.user)

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

    def clean_profile_image(self):
        """Validate profile image file."""
        from django.core.exceptions import ValidationError

        image = self.cleaned_data.get("profile_image")
        if not image:
            return image

        # Check file size (5MB max)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if image.size > max_size:
            raise ValidationError(_("Image file too large. Maximum size is 5MB."))

        # Check file format
        allowed_formats = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/heic",
            "image/heif",
            "image/jxl",  # JPEG XL
            "image/jp2",  # JPEG 2000
        }
        if image.content_type not in allowed_formats:
            raise ValidationError(
                _(
                    "Unsupported image format. "
                    "Allowed formats: JPEG, PNG, WebP, HEIC/HEIF, JPEGXL, JPEG2000."
                )
            )

        return image


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


# forms.py (add below your EditProfileForm or near the formset)
ALLOWED_URL_SCHEMES = {"http", "https"}


def normalize_http_url(raw: str) -> str:
    if not raw:
        return raw
    s = nh3.clean(raw.strip())

    # Add default scheme if missing
    if "://" not in s and not s.startswith(("http://", "https://")):
        s = f"https://{s}"

    parsed = urlparse(s)
    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_URL_SCHEMES:
        raise forms.ValidationError("Only http(s) URLs are allowed.")

    netloc = parsed.netloc.lower()
    path = quote(unquote(parsed.path or ""))

    # Optional: drop common tracking params
    params = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if not k.lower().startswith("utm_")
    ]
    query = urlencode(params, doseq=True)

    # Optional: strip fragments; keep if you want
    fragment = ""

    return urlunparse((scheme, netloc, path, "", query, fragment))


class UserProfileLinkForm(forms.ModelForm):
    class Meta:
        model = UserProfileLink
        fields = ("position", "url")
        widgets = {
            "url": forms.URLInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "https://example.com/profile",
                }
            )
        }

    def clean_url(self):
        url = self.cleaned_data.get("url", "")
        if not url:
            return url
        return normalize_http_url(url)


class BaseUserProfileLinkFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        seen = set()
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if self.can_delete and form.cleaned_data.get("DELETE"):
                continue
            url = form.cleaned_data.get("url")
            if not url:
                continue
            if url in seen:
                form.add_error("url", "Duplicate URL.")
            seen.add(url)


# Formset for managing user profile links
UserProfileLinkFormSet = inlineformset_factory(
    UserProfile,
    UserProfileLink,
    form=UserProfileLinkForm,
    formset=BaseUserProfileLinkFormSet,
    fields=("position", "url"),
    extra=1,
    can_delete=True,
)
