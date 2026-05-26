from django.urls import path
from .views import makeimage_alt

urlpatterns = [
    path(
        'makeimage_alt/',
        makeimage_alt
    )
]