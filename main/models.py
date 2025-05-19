
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django.db import models
from datetime import date, datetime


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), name=name, surname=surname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None):
        user = self.create_user(email=email, name=name, surname=surname, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user




class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    company_code = models.CharField(max_length=255, default="oddiy")
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    default_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Yangi Role maydoni
    ROLE_CHOICES = [
        ('CEO', 'CEO'),
        ('Financial Director', 'Financial Director'),
        ('Member', 'Member'),
        ('Customer', 'Customer'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Customer')

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def __str__(self):
        return self.email


class UserPagePermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_permissions')
    page_name = models.CharField(max_length=100, choices=[
        ('ceo', 'Ceo'),
        ('payment_list', 'Payment'),
        ('project_toggle', 'WordPress'),
        ('crm', 'Sales CRM'),
        ('finance_list', 'Finance'),
    ])

    class Meta:
        unique_together = ('user', 'page_name')

    def __str__(self):
        return f"{self.user.email} - {self.page_name}"


class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_cards')
    card_number = models.CharField(max_length=16, unique=True)  # 16 belgili kredit karta raqami
    is_primary = models.BooleanField(default=False)  # Primary yoki secondary
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'is_primary'], condition=models.Q(is_active=True), name='unique_active_primary_card_per_user'),
            models.UniqueConstraint(fields=['user'], condition=models.Q(is_primary=False, is_active=True), name='unique_active_secondary_card_per_user')
        ]

    def __str__(self):
        return f"{self.user.email} - {'Primary' if self.is_primary else 'Secondary'} Card: {self.card_number[:4]}****"


class MonthlyUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_updates')
    update_date = models.DateField(auto_now_add=True)
    update_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    potential_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.email} - {self.update_date}: {self.update_percentage}% - ${self.potential_monthly}"




class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class Payment(models.Model):
    project = models.CharField(max_length=100)
    date = models.DateField()  # Date field for payment due date
    summ = models.DecimalField(max_digits=19, decimal_places=2)
    payment = models.BooleanField(default=False)  # Changed default to False

    def get_status(self):
        today = date.today()
        due_date = self.date
        days_until_due = (due_date - today).days

        if self.payment:  # To'lov allaqachon qilingan
            return "Paid", "success"
        elif days_until_due < 0:
            return "Unpaid", "danger"
        elif days_until_due <= 3:
            return "Payment Due Soon", "warning"
        else:
            return "Paid", "success"  # 3 kundan ko'p bo‘lsa, hali vaqt bor — avtomatik Paid deb hisoblanadi
