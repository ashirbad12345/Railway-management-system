from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Train(models.Model):
    train_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    source = models.CharField(max_length=100, db_index=True)
    destination = models.CharField(max_length=100, db_index=True)
    total_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    available_seats = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(total_seats__gte=1), name="train_total_seats_positive"),
            models.CheckConstraint(condition=models.Q(available_seats__lte=models.F("total_seats")), name="train_available_seats_valid"),
        ]


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    train = models.ForeignKey(Train, on_delete=models.PROTECT, related_name="bookings")
    seats = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    booking_reference = models.CharField(max_length=16, unique=True, editable=False)
    status = models.CharField(max_length=20, default="CONFIRMED")
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-booked_at"]
