from django.shortcuts import render


def home(request):
    """Home page view."""
    return render(request, "index.html")


def custom_404(request):
    """Custom 404 page view."""
    return render(request, "404.html", status=404)
