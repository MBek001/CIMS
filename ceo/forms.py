from django import forms
from ceo.models import Customer, Finance
from main.models import Message
from django import forms
from django.contrib.auth import get_user_model
from main.models import UserPagePermission
from django import forms
from main.models import User, UserPagePermission
from django import forms
from decimal import Decimal



User = get_user_model()


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'body']
        widgets = {
            'receiver': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
        }


class MessageFormAll(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'id': 'floatingFullName'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'id': 'floatingUsername'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'id': 'floatingPhoneNumber'
            }),
            'platform': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Platform',
                'id': 'floatingPlatform'
            }),
            'assistant_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assistant Name',
                'id': 'floatingAssistant'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'floatingStatus'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notes...',
                'id': 'floatingNotes',
                'style': 'height: 100px'
            }),
        }

class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['type', 'status', 'card', 'service', 'summ', 'currency', 'date', 'donation_percentage']

    def clean(self):
        cleaned_data = super().clean()
        card = cleaned_data.get('card')
        currency = cleaned_data.get('currency')
        donation_percentage = cleaned_data.get('donation_percentage')

        # Card-based currency validation
        if card and not currency:
            if card in ['card1', 'card2']:
                cleaned_data['currency'] = 'UZS'
            elif card == 'card3':
                cleaned_data['currency'] = 'USD'
            currency = cleaned_data['currency']

        if not currency:
            raise forms.ValidationError("Valyuta tanlanishi kerak.")

        if card in ['card1', 'card2'] and currency != 'UZS':
            raise forms.ValidationError("Company Account UZB va Uzcard faqat UZS qabul qiladi.")
        if card == 'card3' and currency != 'USD':
            raise forms.ValidationError("Company Account US faqat USD qabul qiladi.")

        # Donation percentage validation
        if donation_percentage is not None and (donation_percentage < 0 or donation_percentage > 100):
            raise forms.ValidationError("Donation foizi 0 dan 100 gacha bo'lishi kerak.")

        return cleaned_data


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    page_permissions = forms.MultipleChoiceField(
        choices=[
            ('ceo', 'Dashboard'),
            ('crm', 'Sales CRM'),
            ('payment_list', 'Payment'),
            ('finance_list', 'Finance'),
            ('project_toggle', 'Wordpress'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    is_active = forms.BooleanField(required=False, label="Active Status")  # Yangi qo'shildi

    class Meta:
        model = User
        fields = ['email', 'name', 'surname', 'role', 'company_code', 'is_active', 'telegram_id', 'default_salary']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Foydalanuvchining mavjud ruxsatlarini avtomatik belgilash
            permissions = UserPagePermission.objects.filter(user=self.instance).values_list('page_name', flat=True)
            self.fields['page_permissions'].initial = list(permissions)
            self.fields['is_active'].initial = self.instance.is_active  # is_active qiymatini saqlash

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        # Parolni saqlash
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
            user.save()
        # Ruxsatlarni yangilash
        UserPagePermission.objects.filter(user=user).delete()
        selected_pages = self.cleaned_data.get('page_permissions', [])
        for page in selected_pages:
            UserPagePermission.objects.create(user=user, page_name=page)
        return user