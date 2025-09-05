from django.http import HttpResponse
from django.shortcuts import redirect, render

from agora.apps.core.forms import WaitlistSignupForm


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
            # For now, just return success message
            # TODO: Save to database, send email, etc.
            return HttpResponse("Form submitted successfully!", status=200)
        else:
            # For now, return validation errors
            # TODO: Return proper error response or redirect with errors
            return HttpResponse(f"Form validation failed: {form.errors}", status=400)

    # Fallback for other methods
    return HttpResponse("Method not allowed", status=405)


def custom_404(request):
    """Custom 404 page view."""
    return render(request, "404.html", status=404)
