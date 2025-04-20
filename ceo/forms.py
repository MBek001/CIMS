from django import forms

from ceo.models import Customer
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
