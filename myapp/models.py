from django.db import models


class Location(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Location name (e.g., Library, CS Lab)"
    )

    building = models.CharField(
        max_length=100,
        help_text="Building name (e.g., Block A)"
    )

    floor = models.CharField(
        max_length=50,
        help_text="Floor number (e.g., Ground Floor, 2nd Floor)"
    )

    description = models.TextField(
        blank=True,
        help_text="Additional details about the location"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Location"
        verbose_name_plural = "Locations"