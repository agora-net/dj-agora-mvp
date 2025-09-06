from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from agora.apps.core.forms import WaitlistSignupForm
from agora.apps.core.models import WaitingList
from agora.apps.core.services import add_to_waiting_list


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


class SignupViewTestCase(TestCase):
    """
    Test cases for the signup view functionality.
    """

    def test_successful_signup_redirects_to_detail_view(self):
        """
        Test that successful signup redirects to the signup detail view.
        """
        form_data = {"email": "test@example.com"}
        response = self.client.post(reverse("signup"), data=form_data)

        # Should redirect to the signup status page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/signup/"))

        # Follow the redirect to verify the detail view works
        detail_response = self.client.get(response.url)
        self.assertEqual(detail_response.status_code, 200)
        content = detail_response.content.decode()
        self.assertIn("Welcome to the Agora waitlist!", content)
        self.assertIn("Your position in line", content)
        self.assertIn("Bookmark this page", content)

    def test_duplicate_email_redirects_to_existing_position(self):
        """
        Test that signing up with an existing email redirects to their current position.
        """
        # Create an existing waiting list entry
        existing_entry = WaitingList.objects.create(
            email="existing@example.com", invite_code="existing-invite-code"
        )

        # Try to sign up with the same email
        form_data = {"email": "existing@example.com"}
        response = self.client.post(reverse("signup"), data=form_data)

        # Should redirect to the existing entry's position page
        self.assertEqual(response.status_code, 302)
        expected_url = reverse("signup_status", kwargs={"signup_id": existing_entry.id})
        self.assertEqual(response.url, expected_url)

        # Follow the redirect to verify it shows the existing position
        detail_response = self.client.get(response.url)
        self.assertEqual(detail_response.status_code, 200)
        content = detail_response.content.decode()
        self.assertIn("Welcome to the Agora waitlist!", content)
        self.assertIn("Your position in line", content)
        self.assertIn("Bookmark this page", content)
        self.assertIn("existing@example.com", content)

        # Verify no new entry was created
        self.assertEqual(WaitingList.objects.filter(email="existing@example.com").count(), 1)

    def test_signup_status_view_shows_correct_information(self):
        """
        Test that the signup status view shows the correct information.
        """
        # Create a waiting list entry
        waiting_list_entry = WaitingList.objects.create(
            email="test@example.com", invite_code="test-invite-code"
        )

        # Access the signup status view
        response = self.client.get(
            reverse("signup_status", kwargs={"signup_id": waiting_list_entry.id})
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Check that all expected information is present
        self.assertIn("Welcome to the Agora waitlist!", content)
        self.assertIn("Your position in line", content)
        self.assertIn("Bookmark this page", content)
        self.assertIn("test@example.com", content)

        # Check that the position number is present
        self.assertIn(str(waiting_list_entry.waiting_list_position), content)

    def test_signup_status_view_404_for_invalid_uuid(self):
        """
        Test that the signup status view returns 404 for invalid UUID.
        """
        import uuid

        invalid_uuid = uuid.uuid4()

        response = self.client.get(reverse("signup_status", kwargs={"signup_id": invalid_uuid}))

        self.assertEqual(response.status_code, 404)


class WaitingListCachingTestCase(TestCase):
    """
    Test cases for the WaitingList caching functionality.
    """

    def setUp(self):
        """Clear cache before each test."""
        cache.clear()

    def test_pre_cache_position_method(self):
        """
        Test that pre_cache_position method caches the position correctly.
        """
        # Create a waiting list entry
        waiting_list_entry = WaitingList.objects.create(
            email="test@example.com", invite_code="test-invite-code"
        )

        # Verify cache is empty initially
        cache_key = str(waiting_list_entry.type_id)
        self.assertIsNone(cache.get(cache_key))

        # Pre-cache the position
        position = waiting_list_entry.pre_cache_position()

        # Verify position is cached
        cached_position = cache.get(cache_key)
        self.assertEqual(cached_position, position)
        self.assertEqual(cached_position, 1)  # First entry should be position 1

    def test_waiting_list_position_property_uses_cache(self):
        """
        Test that waiting_list_position property uses cached value when available.
        """
        # Create a waiting list entry
        waiting_list_entry = WaitingList.objects.create(
            email="test@example.com", invite_code="test-invite-code"
        )

        # Pre-cache the position
        expected_position = waiting_list_entry.pre_cache_position()

        # Access the position property - should use cached value
        actual_position = waiting_list_entry.waiting_list_position

        self.assertEqual(actual_position, expected_position)
        self.assertEqual(actual_position, 1)

    def test_add_to_waiting_list_pre_caches_position(self):
        """
        Test that add_to_waiting_list service pre-caches the position.
        """
        # Add to waiting list using the service
        waiting_list_entry = add_to_waiting_list("test@example.com")

        # Verify position is cached
        cache_key = str(waiting_list_entry.type_id)
        cached_position = cache.get(cache_key)

        self.assertIsNotNone(cached_position)
        self.assertEqual(cached_position, 1)  # First entry should be position 1

        # Verify accessing the position property uses the cached value
        position = waiting_list_entry.waiting_list_position
        self.assertEqual(position, cached_position)

    def test_multiple_entries_position_caching(self):
        """
        Test position caching with multiple entries.
        """
        # Create first entry
        first_entry = add_to_waiting_list("first@example.com")
        first_position = first_entry.waiting_list_position
        self.assertEqual(first_position, 1)

        # Create second entry
        second_entry = add_to_waiting_list("second@example.com")
        second_position = second_entry.waiting_list_position
        self.assertEqual(second_position, 2)

        # Verify both positions are cached
        first_cache_key = str(first_entry.type_id)
        second_cache_key = str(second_entry.type_id)

        self.assertEqual(cache.get(first_cache_key), 1)
        self.assertEqual(cache.get(second_cache_key), 2)

    def test_invalidate_position_cache(self):
        """
        Test that invalidate_position_cache removes the cached position.
        """
        # Create and pre-cache position
        waiting_list_entry = WaitingList.objects.create(
            email="test@example.com", invite_code="test-invite-code"
        )
        waiting_list_entry.pre_cache_position()

        # Verify position is cached
        cache_key = str(waiting_list_entry.type_id)
        self.assertIsNotNone(cache.get(cache_key))

        # Invalidate cache
        waiting_list_entry.invalidate_position_cache()

        # Verify cache is cleared
        self.assertIsNone(cache.get(cache_key))

    def test_position_never_below_one(self):
        """
        Test that position calculation never returns a value below 1.
        This tests the max(1, people_ahead + 1) logic.
        """
        # Create a waiting list entry
        waiting_list_entry = WaitingList.objects.create(
            email="test@example.com", invite_code="test-invite-code"
        )

        # Verify position is at least 1
        position = waiting_list_entry.waiting_list_position
        self.assertGreaterEqual(position, 1)

        # Verify pre-cached position is also at least 1
        pre_cached_position = waiting_list_entry.pre_cache_position()
        self.assertGreaterEqual(pre_cached_position, 1)

    def test_position_calculation_with_max_logic(self):
        """
        Test that both waiting_list_position and pre_cache_position use max(1, people_ahead + 1).
        """
        # Create a waiting list entry
        waiting_list_entry = WaitingList.objects.create(
            email="test@example.com", invite_code="test-invite-code"
        )

        # Test waiting_list_position property
        position_property = waiting_list_entry.waiting_list_position
        self.assertEqual(position_property, 1)  # First entry should be position 1

        # Test pre_cache_position method
        position_method = waiting_list_entry.pre_cache_position()
        self.assertEqual(position_method, 1)  # First entry should be position 1

        # Both should return the same value
        self.assertEqual(position_property, position_method)

    def test_multiple_entries_position_ordering(self):
        """
        Test that multiple entries get correct positions with max() logic.
        """
        # Create multiple entries
        first_entry = WaitingList.objects.create(
            email="first@example.com", invite_code="first-invite-code"
        )
        second_entry = WaitingList.objects.create(
            email="second@example.com", invite_code="second-invite-code"
        )
        third_entry = WaitingList.objects.create(
            email="third@example.com", invite_code="third-invite-code"
        )

        # Verify positions are correct and >= 1
        self.assertEqual(first_entry.waiting_list_position, 1)
        self.assertEqual(second_entry.waiting_list_position, 2)
        self.assertEqual(third_entry.waiting_list_position, 3)

        # Verify pre-cached positions are also correct
        self.assertEqual(first_entry.pre_cache_position(), 1)
        self.assertEqual(second_entry.pre_cache_position(), 2)
        self.assertEqual(third_entry.pre_cache_position(), 3)

    def test_position_consistency_between_property_and_method(self):
        """
        Test that waiting_list_position property and pre_cache_position method
        return consistent results.
        """
        # Create a waiting list entry
        waiting_list_entry = WaitingList.objects.create(
            email="test@example.com", invite_code="test-invite-code"
        )

        # Clear any existing cache
        cache_key = str(waiting_list_entry.type_id)
        cache.delete(cache_key)

        # Get position from property (should calculate and cache)
        position_from_property = waiting_list_entry.waiting_list_position

        # Get position from method (should use same logic)
        position_from_method = waiting_list_entry.pre_cache_position()

        # Both should return the same value
        self.assertEqual(position_from_property, position_from_method)
        self.assertEqual(position_from_property, 1)
        self.assertEqual(position_from_method, 1)
