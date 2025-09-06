from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from agora.apps.core.forms import WaitlistSignupForm
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
                return HttpResponse(
                    f"Successfully added to waiting list! "
                    f"Your position: #{waiting_list_entry.waiting_list_position}, "
                    f"Your invite code: {waiting_list_entry.invite_code}",
                    status=200,
                )
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


def custom_404(request):
    """Custom 404 page view."""
    return render(request, "404.html", status=404)
