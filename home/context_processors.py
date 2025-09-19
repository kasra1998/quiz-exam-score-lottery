from .models import Types

def categories_context(request):
    """Make categories available in all templates."""
    return {
        "categories": Types.objects.all()
    }
