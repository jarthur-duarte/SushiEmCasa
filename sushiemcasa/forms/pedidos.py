from django import forms
from sushiemcasa.models import Order 
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from sushiemcasa.horarios import motivo_recusa

class OrderForm(forms.ModelForm):
    delivery_datetime = forms.DateTimeField(
        label="Pickup date and time",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True,
        error_messages={'required': 'Choose a pickup date and time.'},
        help_text="Pick one of the available pickup times (minimum 24 hours in advance)."
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
           
            # Mesma regra que monta a lista de horários do checkout (sushiemcasa/horarios.py),
            # baseada no horário de funcionamento definido no painel.
            motivo = motivo_recusa(delivery_dt_aware)
            if motivo:
                raise forms.ValidationError(motivo)

            feriados = [
                datetime.date(2024, 12, 25),
                datetime.date(2025, 1, 1),
                datetime.date(2025, 12, 25) 
            ]
            if delivery_dt_aware.date() in feriados:
                raise forms.ValidationError(f"Pickup is not available on {delivery_dt_aware.strftime('%m/%d/%Y')}.")
            
            return delivery_dt_aware 
        return delivery_dt 