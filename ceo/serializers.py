from rest_framework import serializers
from ceo.models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [ 'full_name', 'platform', 'username', 'phone_number', 'status', 'assistant_name', 'notes']