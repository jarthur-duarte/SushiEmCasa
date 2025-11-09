from django import forms
from sushiemcasa.models import Order 
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

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
            
            delivery_dt_aware = delivery_dt
            if timezone.is_naive(delivery_dt):
             
                delivery_dt_aware = timezone.make_aware(delivery_dt, timezone.get_current_timezone())
           
            now_plus_24h = timezone.now() + datetime.timedelta(hours=24)
            
           
            if delivery_dt_aware < now_plus_24h:
                raise forms.ValidationError("Delivery date must be at least 24 hours in advance.")
            
            if delivery_dt_aware.weekday() == 6: 
                raise forms.ValidationError("Sorry, we do not deliver on Sundays.")
            
            hora = delivery_dt_aware.time()
            if hora < datetime.time(10, 0) or hora >= datetime.time(20, 0):
                raise forms.ValidationError("Our delivery times are between 10:00 and 20:00.")
            
            feriados = [
                datetime.date(2024, 12, 25),
                datetime.date(2025, 1, 1),
                datetime.date(2025, 12, 25) 
            ]
            if delivery_dt_aware.date() in feriados:
                raise forms.ValidationError(f"Não realizamos entregas no dia {delivery_dt_aware.strftime('%d/%m/%Y')}.")
            
            return delivery_dt_aware 
        return delivery_dt 