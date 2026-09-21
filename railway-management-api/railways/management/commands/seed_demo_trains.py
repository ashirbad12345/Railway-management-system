from django.core.management.base import BaseCommand

from railways.models import Train


class Command(BaseCommand):
    help = "Create sample trains for local development if they do not exist."

    trains = [
        ("12951", "Rajdhani Express", "Delhi", "Mumbai", 120),
        ("12011", "Shatabdi Express", "Delhi", "Chandigarh", 80),
        ("12123", "Deccan Queen", "Mumbai", "Pune", 100),
        ("12841", "Coromandel Express", "Kolkata", "Chennai", 150),
        ("20607", "Vande Bharat", "Bengaluru", "Chennai", 96),
    ]

    def handle(self, *args, **options):
        created = 0
        for train_number, name, source, destination, total_seats in self.trains:
            _, was_created = Train.objects.get_or_create(
                train_number=train_number,
                defaults={
                    "name": name,
                    "source": source,
                    "destination": destination,
                    "total_seats": total_seats,
                    "available_seats": total_seats,
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Demo trains ready. Created {created} new train(s)."))
