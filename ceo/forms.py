from django import forms

from ceo.models import Customer, Finance
from main.models import Message

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



from django import forms
from .models import Finance

class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['type', 'status', 'card', 'service', 'summ', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'summ': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        summ = cleaned_data.get('summ')
        if summ is not None and summ <= 0:
            self.add_error('summ', 'Amount must be positive')
        return cleaned_data