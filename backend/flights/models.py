from django.db import models


class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    logo = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Flight(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    flight_number = models.CharField(max_length=20)
    aircraft = models.CharField(max_length=100, blank=True, null=True)
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departure_flights')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrival_flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_seats = models.IntegerField()
    is_direct = models.BooleanField(default=True)
    is_shared = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.airline} {self.flight_number}"
