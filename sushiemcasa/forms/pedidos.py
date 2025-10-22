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
            now_plus_24h = timezone.now() + datetime.timedelta(hours=24)
            if delivery_dt < now_plus_24h:
                raise forms.ValidationError("A data de entrega deve ter pelo menos 24 horas de antecedência.")
            if delivery_dt.weekday() == 6:
                raise forms.ValidationError("Desculpe, não realizamos entregas aos domingos.")
            hora = delivery_dt.time()
            if hora < datetime.time(10, 0) or hora >= datetime.time(20, 0):
                raise forms.ValidationError("Nosso horário de entrega é entre 10:00 e 20:00.")
            feriados = [
                    datetime.date(2024, 12, 25),
                    datetime.date(2025, 1, 1),
                    datetime.date(2025, 12, 25) 
                ]
            if delivery_dt.date() in feriados:
                raise forms.ValidationError(f"Não realizamos entregas no dia {delivery_dt.strftime('%d/%m/%Y')}.")
        return delivery_dt