from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import AvailabilityView, BookingCreateView, BookingDetailView, BookingListView, RegisterView, TrainCatalogView, TrainCreateView, TrainSearchView, TrainUpdateView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("trains/", TrainSearchView.as_view(), name="train-search"),
    path("trains/catalog/", TrainCatalogView.as_view(), name="train-catalog"),
    path("admin/trains/", TrainCreateView.as_view(), name="admin-train-create"),
    path("admin/trains/<int:pk>/", TrainUpdateView.as_view(), name="admin-train-update"),
    path("trains/<int:pk>/", TrainUpdateView.as_view(), name="train-update"),
    path("trains/availability/", AvailabilityView.as_view(), name="availability"),
    path("trains/<int:train_id>/bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/", BookingListView.as_view(), name="booking-list"),
    path("bookings/<int:pk>/", BookingDetailView.as_view(), name="booking-detail"),
]
