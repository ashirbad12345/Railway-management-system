from django.db import IntegrityError, transaction
from django.db.models import F
from django.views.generic import TemplateView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Train
from .permissions import HasAdminAPIKey
from .serializers import BookingSerializer, RegisterSerializer, TrainSerializer


class DashboardView(TemplateView):
    template_name = "railways/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["trains"] = Train.objects.all()
        return context


class AdminDashboardView(TemplateView):
    template_name = "railways/admin_dashboard.html"


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class TrainCreateView(generics.CreateAPIView):
    permission_classes = [HasAdminAPIKey]
    authentication_classes = []
    serializer_class = TrainSerializer


class TrainCatalogView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = TrainSerializer
    queryset = Train.objects.all()


class TrainSearchView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = TrainSerializer

    def get_queryset(self):
        queryset = Train.objects.all()
        source = self.request.query_params.get("source", "").strip()
        destination = self.request.query_params.get("destination", "").strip()
        if source:
            queryset = queryset.filter(source__iexact=source)
        if destination:
            queryset = queryset.filter(destination__iexact=destination)
        return queryset


class TrainUpdateView(generics.UpdateAPIView):
    permission_classes = [HasAdminAPIKey]
    authentication_classes = []
    serializer_class = TrainSerializer
    queryset = Train.objects.all()


class AvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        source = request.query_params.get("source", "").strip()
        destination = request.query_params.get("destination", "").strip()
        if not source or not destination:
            return Response({"detail": "source and destination query parameters are required."}, status=400)
        trains = Train.objects.filter(source__iexact=source, destination__iexact=destination)
        return Response(TrainSerializer(trains, many=True).data)


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, train_id):
        seats = request.data.get("seats", 1)
        try:
            seats = int(seats)
        except (TypeError, ValueError):
            return Response({"detail": "seats must be a positive integer."}, status=400)
        if seats < 1:
            return Response({"detail": "seats must be a positive integer."}, status=400)

        try:
            with transaction.atomic():
                train = Train.objects.select_for_update().get(pk=train_id)
                if train.available_seats < seats:
                    return Response({"detail": "Not enough seats available."}, status=status.HTTP_409_CONFLICT)
                train.available_seats = F("available_seats") - seats
                train.save(update_fields=["available_seats", "updated_at"])
                train.refresh_from_db()
                booking = Booking.objects.create(
                    user=request.user,
                    train=train,
                    seats=seats,
                    booking_reference=BookingSerializer.create_reference(),
                )
        except Train.DoesNotExist:
            return Response({"detail": "Train not found."}, status=404)
        except IntegrityError:
            return Response({"detail": "Could not create booking."}, status=409)
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class BookingDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("train", "user")


class BookingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related("train", "user")
