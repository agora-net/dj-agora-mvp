from django.test import TestCase

from agora.apps.core.forms import WaitlistSignupForm


class WaitlistSignupFormTestCase(TestCase):
    """
    Test cases for the WaitlistSignupForm.
    """

    def test_form_has_correct_fields(self):
        """
        Test that the form has the expected email field.
        """
        form = WaitlistSignupForm()
        self.assertIn("email", form.fields)

    def test_email_field_attributes(self):
        """
        Test that the email field has the correct attributes.
        """
        form = WaitlistSignupForm()
        email_field = form.fields["email"]

        self.assertEqual(email_field.label, "Email address")
        self.assertEqual(email_field.max_length, 254)
        self.assertEqual(
            email_field.help_text,
            "We'll notify you when Agora is ready for you to use.",
        )

    def test_email_widget_attributes(self):
        """
        Test that the email field widget has the correct CSS classes and attributes.
        """
        form = WaitlistSignupForm()
        email_widget = form.fields["email"].widget

        self.assertEqual(
            email_widget.attrs["class"],
            "input input-bordered w-full",
        )
        self.assertEqual(
            email_widget.attrs["placeholder"],
            "Enter your email address",
        )
        self.assertTrue(email_widget.attrs["required"])

    def test_valid_email_submission(self):
        """
        Test form validation with a valid email address.
        """
        form_data = {"email": "test@example.com"}
        form = WaitlistSignupForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "test@example.com")

    def test_invalid_email_submission(self):
        """
        Test form validation with an invalid email address.
        """
        form_data = {"email": "invalid-email"}
        form = WaitlistSignupForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_empty_email_submission(self):
        """
        Test form validation with an empty email address.
        """
        form_data = {"email": ""}
        form = WaitlistSignupForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_missing_email_submission(self):
        """
        Test form validation with missing email field.
        """
        form_data = {}
        form = WaitlistSignupForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_normalization_lowercase(self):
        """
        Test that email addresses are normalized to lowercase.
        """
        form_data = {"email": "TEST@EXAMPLE.COM"}
        form = WaitlistSignupForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "test@example.com")

    def test_email_normalization_whitespace(self):
        """
        Test that email addresses have whitespace trimmed.
        """
        form_data = {"email": "  test@example.com  "}
        form = WaitlistSignupForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "test@example.com")

    def test_email_normalization_combined(self):
        """
        Test that email addresses are both lowercased and trimmed.
        """
        form_data = {"email": "  TEST@EXAMPLE.COM  "}
        form = WaitlistSignupForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["email"], "test@example.com")

    def test_email_max_length_validation(self):
        """
        Test that email addresses exceeding max length are rejected.
        """
        # Create an email that's longer than 254 characters
        long_local = "a" * 250
        form_data = {"email": f"{long_local}@example.com"}
        form = WaitlistSignupForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_various_valid_email_formats(self):
        """
        Test that various valid email formats are accepted.
        """
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user123@example.co.uk",
            "test@subdomain.example.com",
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                form_data = {"email": email}
                form = WaitlistSignupForm(data=form_data)
                self.assertTrue(
                    form.is_valid(),
                    f"Email '{email}' should be valid but form errors: {form.errors}",
                )

    def test_various_invalid_email_formats(self):
        """
        Test that various invalid email formats are rejected.
        """
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
            "user@example..com",
            "user@example",
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                form_data = {"email": email}
                form = WaitlistSignupForm(data=form_data)
                self.assertFalse(
                    form.is_valid(),
                    f"Email '{email}' should be invalid but form is valid",
                )
