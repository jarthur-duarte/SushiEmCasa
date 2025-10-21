from django import forms
from sushiemcasa.models import Order 
import datetime
from django.utils import timezone

class OrderForm(forms.ModelForm):
    delivery_datetime = forms.DateTimeField(
        label="Delivery Date and Time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        help_text="Select the desired date and time for delivery (minimum 24 hours in advance)."
    )

    class Meta:
        model = Order
        fields = ['delivery_datetime']

    def clean_delivery_datetime(self):
        delivery_dt = self.cleaned_data.get('delivery_datetime')
        if delivery_dt:
            now_plus_24h = timezone.now() + datetime.timedelta(hours=24)
            if delivery_dt.astimezone(timezone.get_current_timezone()) < now_plus_24h:
                raise forms.ValidationError("The delivery date must be at least 24 hours in the future.")
        return delivery_dt