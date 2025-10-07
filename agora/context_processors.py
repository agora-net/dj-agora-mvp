from django.conf import settings


def stripe_publishable_key(request):
    """
    Context processor that makes STRIPE_PUBLISHABLE_KEY available in all templates.
    """
    return {
        "STRIPE_PUBLISHABLE_KEY": getattr(settings, "STRIPE_PUBLISHABLE_KEY", ""),
    }
