from django.db import models
from django.db import models
from decimal import Decimal
import requests
from django.utils import timezone



class Payment(models.Model):
    project = models.CharField(max_length=100)
    payment = models.BooleanField(default=True)


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
        ('need_to_call', 'Need to Call'),  # Yangi status qo'shildi
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
    TYPE_CHOICES = [
        ('incomer', 'Income'),
        ('outcomer', 'Outcome'),
    ]
    STATUS_CHOICES = [
        ('one_time', 'One-Time'),
        ('monthly', 'Monthly'),
    ]
    CARD_CHOICES = [
        ('card1', 'Company Account UZB'),
        ('card2', 'Uzcard UZB'),
        ('card3', 'Company Account US'),
    ]
    CURRENCY_CHOICES = [
        ('UZS', 'UZS'),
        ('USD', 'USD'),
    ]
    TRANSACTION_STATUS = [
        ('real', 'Real'),
        ('statistical', 'Statistical'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    card = models.CharField(max_length=20, choices=CARD_CHOICES)
    service = models.CharField(max_length=255)
    summ = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    date = models.DateField()
    donation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    donation_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)  # Only for transfers
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    transaction_status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='statistical')
    initial_date = models.DateField(null=True, blank=True)  # Birinchi kiritilgan sanani saqlash uchun

    def save(self, *args, **kwargs):
        today = timezone.now().date()
        # Agar yangi tranzaksiya bo'lsa, initial_date ni o'rnatamiz
        if not self.pk:  # Yangi yozuv yaratilayotgan bo'lsa
            self.initial_date = self.date
            if self.date == today:
                self.transaction_status = 'real'
            else:
                self.transaction_status = 'statistical'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service} - {self.summ} {self.currency}"


class DonationBalance(models.Model):
    total_donation = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    @classmethod
    def get_or_create(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class ExchangeRate(models.Model):
    usd_to_uzs = models.DecimalField(max_digits=15, decimal_places=2, default=12700.00)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_current_rate(cls):
        try:
            api_key = "96bf9d00895a4b7581598aa03774dcd7"
            response = requests.get(f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}")
            response.raise_for_status()
            data = response.json()
            usd_to_uzs = Decimal(data["rates"]["UZS"])
            obj, created = cls.objects.get_or_create(pk=1)
            obj.usd_to_uzs = usd_to_uzs
            obj.save()
            return usd_to_uzs
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            obj, created = cls.objects.get_or_create(pk=1)
            return obj.usd_to_uzs