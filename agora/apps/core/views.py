from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from agora.apps.core.forms import WaitlistSignupForm
from agora.apps.core.models import WaitingList
from agora.apps.core.services import add_to_waiting_list


def home(request):
    """
    Home page view with waitlist signup form.
    """
    form = WaitlistSignupForm()
    return render(request, "index.html", {"form": form})


def signup(request):
    """
    Signup view for waitlist form submission.

    GET: Redirects to home page
    POST: Validates the waitlist signup form
    """
    if request.method == "GET":
        return redirect("home")

    if request.method == "POST":
        form = WaitlistSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            # Check if email already exists
            try:
                existing_entry = WaitingList.objects.get(email=email)
                # Email already exists - redirect to their existing position
                return redirect("signup_status", signup_id=existing_entry.id)
            except WaitingList.DoesNotExist:
                # Email doesn't exist, create new entry
                try:
                    waiting_list_entry = add_to_waiting_list(email)
                    # Redirect to the signup detail view showing their position and UUID
                    return redirect("signup_status", signup_id=waiting_list_entry.id)
                except IntegrityError:
                    # Race condition - email was added between our check and creation
                    # Try to get the existing entry again
                    existing_entry = WaitingList.objects.get(email=email)
                    return redirect("signup_status", signup_id=existing_entry.id)
                except ValueError as e:
                    return HttpResponse(f"Invalid email address: {e}", status=400)
        else:
            # Return form validation errors
            return HttpResponse(f"Form validation failed: {form.errors}", status=400)

    # Fallback for other methods
    return HttpResponse("Method not allowed", status=405)


def signup_status(request, signup_id):
    """
    View to show waiting list details for a specific signup ID.

    Args:
        signup_id: The UUID of the waiting list entry

    Returns:
        Rendered HTML template with position, UUID, and invite code information or 404 if not found
    """
    try:
        # Look up the waiting list entry by ID
        waiting_list_entry = get_object_or_404(WaitingList, id=signup_id)

        # Render the signup template with the waiting list entry
        return render(request, "signup.html", {"waiting_list_entry": waiting_list_entry})
    except Http404:
        # This will be handled by get_object_or_404, but we can add custom logic here if needed
        raise


def custom_404(request):
    """Custom 404 page view."""
    return render(request, "404.html", status=404)
