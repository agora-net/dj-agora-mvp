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


class EditProfileForm(forms.Form):
    """Form for a user to manage their profile attributes."""

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
        label="Donation amount (USD)",
        min_value=1000,
        widget=forms.NumberInput(
            attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Enter donation amount (minimum $10.00)",
                "required": True,
                "min": "1000",
            }
        ),
        help_text="Minimum donation is $10.00.",
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
            raise forms.ValidationError("Minimum donation amount is $10.00.")
        return amount_cents
