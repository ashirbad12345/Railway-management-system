from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Train",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("train_number", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=150)),
                ("source", models.CharField(db_index=True, max_length=100)),
                ("destination", models.CharField(db_index=True, max_length=100)),
                ("total_seats", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("available_seats", models.PositiveIntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("seats", models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ("booking_reference", models.CharField(editable=False, max_length=16, unique=True)),
                ("status", models.CharField(default="CONFIRMED", max_length=20)),
                ("booked_at", models.DateTimeField(auto_now_add=True)),
                ("train", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="railways.train")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-booked_at"]},
        ),
        migrations.AddConstraint(
            model_name="train",
            constraint=models.CheckConstraint(condition=models.Q(total_seats__gte=1), name="train_total_seats_positive"),
        ),
        migrations.AddConstraint(
            model_name="train",
            constraint=models.CheckConstraint(condition=models.Q(available_seats__lte=models.F("total_seats")), name="train_available_seats_valid"),
        ),
    ]
