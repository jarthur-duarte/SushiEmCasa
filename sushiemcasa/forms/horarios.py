from django import forms
from sushiemcasa.models import HorarioDeFuncionamento

class HorarioForm(forms.ModelForm):
    class Meta:
        model = HorarioDeFuncionamento
        fields = ['is_open', 'open_time', 'close_time']
        
        widgets = {
            'open_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'close_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }