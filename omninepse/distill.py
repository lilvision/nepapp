from django.urls import reverse

def get_urls():
    return [
        reverse('homepage'),
        reverse('display_stocks'),
        reverse('display_floor'),
        # Add other static URLs if needed
    ]
