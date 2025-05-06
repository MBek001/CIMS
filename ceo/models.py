from django.db import models

class Payment(models.Model):
    project = models.CharField(max_length=100)
    payment = models.BooleanField(default=True)



# Create your models here.

class SiteControl(models.Model):
    is_site_on = models.BooleanField(default=True)

    def __str__(self):
        return "Website is ON" if self.is_site_on else "Website is OFF"

class Customer(models.Model):
    STATUS_CHOICES = [
        ('contacted', 'Contacted'),
        ('project_started', 'Project_Started'),
        ('continuing', 'Continuing'),
        ('finished', 'Finished'),
        ('rejected', 'Rejected'),
    ]

    full_name = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    assistant_name = models.CharField(max_length=255)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name



class Finance(models.Model):
    STATUS_CHOICES = [
        ('one_time', 'One_Time'),
        ('monthly', 'Monthly'),
    ]
    TYPE_CHOICES = [
        ('incomer', 'Income'),
        ('outcomer', 'Outcome'),
    ]
    service=models.CharField(max_length=100)
    summ=models.CharField(max_length=100)
    status=models.CharField(max_length=50,choices=STATUS_CHOICES)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    date=models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

