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
            try:
                # Save the email to the waiting list using the service
                waiting_list_entry = add_to_waiting_list(form.cleaned_data["email"])
                # Redirect to the signup detail view showing their position and UUID
                return redirect("signup_status", signup_id=waiting_list_entry.id)
            except IntegrityError:
                return HttpResponse(
                    "This email address is already on our waiting list.",
                    status=400,
                )
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
        HttpResponse with position, UUID, and invite code information or 404 if not found
    """
    try:
        # Look up the waiting list entry by ID
        waiting_list_entry = get_object_or_404(WaitingList, id=signup_id)

        # Return comprehensive waiting list information
        return HttpResponse(
            f"Successfully added to waiting list!\n\n"
            f"Your position: #{waiting_list_entry.waiting_list_position}\n"
            f"Your UUID: {waiting_list_entry.id}\n"
            f"Your invite code: {waiting_list_entry.invite_code}\n"
            f"Your TypeID: {waiting_list_entry.type_id}\n\n"
            f"You can bookmark this URL to check your position anytime: "
            f"{request.build_absolute_uri()}",
            status=200,
        )
    except Http404:
        # This will be handled by get_object_or_404, but we can add custom logic here if needed
        raise


def custom_404(request):
    """Custom 404 page view."""
    return render(request, "404.html", status=404)
