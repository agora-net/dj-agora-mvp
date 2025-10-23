import unicodedata

import nh3
from django import forms
from django.core import validators
from django.utils.translation import gettext_lazy as _

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
            validate_handle_available,
        ],
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

    def clean(self):
        """Clean the form data by sanitizing the string values using nh3."""
        cleaned_data = super().clean()
        for field in self.fields:
            value = cleaned_data.get(field)
            if isinstance(value, str):
                cleaned_data[field] = nh3.clean(value.strip())
        return cleaned_data


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
