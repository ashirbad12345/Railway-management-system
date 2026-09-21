import secrets

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Booking, Train

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "train_number", "name", "source", "destination", "total_seats", "available_seats", "created_at", "updated_at")
        read_only_fields = ("id", "available_seats", "created_at", "updated_at")

    def validate(self, attrs):
        source = attrs.get("source", self.instance.source if self.instance else "")
        destination = attrs.get("destination", self.instance.destination if self.instance else "")
        if source.strip().casefold() == destination.strip().casefold():
            raise serializers.ValidationError("Source and destination must be different.")
        if self.instance and "total_seats" in attrs:
            booked_seats = self.instance.total_seats - self.instance.available_seats
            if attrs["total_seats"] < booked_seats:
                raise serializers.ValidationError("total_seats cannot be lower than seats already booked.")
        return attrs

    def create(self, validated_data):
        validated_data["available_seats"] = validated_data["total_seats"]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "total_seats" in validated_data:
            booked_seats = instance.total_seats - instance.available_seats
            validated_data["available_seats"] = validated_data["total_seats"] - booked_seats
        return super().update(instance, validated_data)


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    train = serializers.PrimaryKeyRelatedField(read_only=True)
    train_number = serializers.CharField(source="train.train_number", read_only=True)
    train_name = serializers.CharField(source="train.name", read_only=True)
    source = serializers.CharField(source="train.source", read_only=True)
    destination = serializers.CharField(source="train.destination", read_only=True)

    class Meta:
        model = Booking
        fields = ("id", "booking_reference", "user", "train", "train_number", "train_name", "source", "destination", "seats", "status", "booked_at")
        read_only_fields = fields

    @staticmethod
    def create_reference():
        return secrets.token_hex(8).upper()
