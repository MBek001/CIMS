from django.db import models

class Payment(models.Model):
    project = models.CharField(max_length=100)
    payment = models.BooleanField(default=True)



# Create your models here.

class SiteControl(models.Model):
    is_site_on = models.BooleanField(default=True)

    def __str__(self):
        return "Website is ON" if self.is_site_on else "Website is OFF"