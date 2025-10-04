import nh3
import structlog
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AcceptInviteForm, WaitlistSignupForm
from .models import WaitingList
from .selectors import get_waiting_list_count, get_waiting_list_entry
from .services import (
    add_to_waiting_list,
    expire_waiting_list_entry,
    register_user,
    validate_cloudflare_turnstile,
)

logger = structlog.get_logger(__name__)


def home(request):
    """
    Home page view with waitlist signup form.
    """
    form = WaitlistSignupForm()
    context = {
        "form": form,
        "waiting_list_count": get_waiting_list_count(),
        "has_signed_up": False,
        "signup_id": None,
    }

    # Check if user has already signed up in this session
    signup_id = request.session.get("signup_id")
    if signup_id:
        try:
            # Verify the signup still exists
            waiting_list_entry = WaitingList.objects.get(id=signup_id)
            context.update(
                {
                    "has_signed_up": True,
                    "signup_id": signup_id,
                    "waiting_list_entry": waiting_list_entry,
                }
            )
        except WaitingList.DoesNotExist:
            # Signup no longer exists, clear from session
            del request.session["signup_id"]

    return render(request, "index.html", context)


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

        # Validate with Cloudflare Turnstile
        token = request.POST.get("cf-turnstile-response")
        secret = settings.CLOUDFLARE_TURNSTILE_SECRET

        remoteip = request.META.get("REMOTE_ADDR")
        if not validate_cloudflare_turnstile(token=token, secret=secret, remoteip=remoteip):
            return HttpResponse("Turnstile validation failed", status=400)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # Check if email already exists
            try:
                existing_entry = WaitingList.objects.get(email=email)
                # Store signup_id in session for future visits
                request.session["signup_id"] = str(existing_entry.id)
                # Email already exists - redirect to their existing position
                return redirect("signup_status", signup_id=existing_entry.id)
            except WaitingList.DoesNotExist:
                # Email doesn't exist, create new entry
                try:
                    waiting_list_entry = add_to_waiting_list(email)
                    # Store signup_id in session for future visits
                    request.session["signup_id"] = str(waiting_list_entry.id)
                    # Redirect to the signup detail view showing their position and UUID
                    return redirect("signup_status", signup_id=waiting_list_entry.id)
                except IntegrityError:
                    # Race condition - email was added between our check and creation
                    # Try to get the existing entry again
                    existing_entry = WaitingList.objects.get(email=email)
                    # Store signup_id in session for future visits
                    request.session["signup_id"] = str(existing_entry.id)
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


def login(request):
    """
    Login view that redirects to the OIDC provider.
    Constructs the OIDC authorization URL and redirects the user.
    """
    # Extract the url from next or default to dashboard
    next_url = request.GET.get("next", "dashboard")
    if request.user.is_authenticated:
        return redirect(next_url)
    # If the user is not authenticated, redirect to the OIDC provider with the next url
    return redirect(reverse("oidc_authentication_init") + "?next=" + next_url)


@login_required
def dashboard(request):
    """
    Dashboard view that requires authentication.
    Shows a placeholder dashboard for authenticated users.
    """
    context = {
        "user": request.user,
    }
    return render(request, "dashboard.html", context)


def invite(request: HttpRequest):
    """
    View to handle invite lookups by invite code.

    Returns:
        When a GET request: Template to gather missing information.
        When a POST request: Handle the invite request.
    """

    if request.method == "GET":
        unsanitized_email = request.GET.get("email", "").strip()
        if not unsanitized_email:
            return HttpResponse("Email is required", status=400)

        unsanitized_invite_code = request.GET.get("invite_code", "").strip()
        if not unsanitized_invite_code:
            return HttpResponse("Invite code is required", status=400)

        sanitized_email = nh3.clean(unsanitized_email)
        sanitized_invite_code = nh3.clean(unsanitized_invite_code)

        waiting_list_entry = get_waiting_list_entry(
            email=sanitized_email,
            invite_code=sanitized_invite_code,
        )
        if not waiting_list_entry:
            raise Http404("Waiting list entry not found")

        form = AcceptInviteForm()
        return render(
            request,
            "invite.html",
            {
                "form": form,
                "waiting_list_entry": waiting_list_entry,
            },
        )

    elif request.method == "POST":
        form = AcceptInviteForm(request.POST)

        # Sanitize the form data
        cleaned_email = form.cleaned_data["email"]
        cleaned_invite_code = form.cleaned_data["invite_code"]
        cleaned_name = form.cleaned_data["name"]
        cleaned_handle = form.cleaned_data["handle"]

        if form.is_valid():
            waiting_list_entry = get_waiting_list_entry(
                email=cleaned_email,
                invite_code=cleaned_invite_code,
            )
            if not waiting_list_entry:
                raise Http404("Waiting list entry not found")

            register_user(
                sanitized_email=cleaned_email,
                sanitized_name=cleaned_name,
                sanitized_handle=cleaned_handle,
                redirect_uri=request.build_absolute_uri(reverse("verify_identity")),
            )

            expire_waiting_list_entry(waiting_list_entry=waiting_list_entry)

            # Show the user that they need to verify their email and set a password.
            # They will be redirected to verify identity page after.

            return render(
                request,
                "core/invite_success.html",
                {
                    "handle": cleaned_handle,
                },
            )

        return render(
            request,
            "invite.html",
            {
                "form": form,
            },
        )

    else:
        return HttpResponse("Method not allowed", status=405)
