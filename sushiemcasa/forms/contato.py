# sushiemcasa/forms/contato.py

from django import forms
# O import do modelo também precisa seguir sua estrutura customizada
from sushiemcasa.models.contato import MensagemFeedback 

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = MensagemFeedback
        fields = ['nome', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Seu nome (opcional)'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Seu email (opcional)'}),
            'mensagem': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Deixe seu feedback aqui...'}),
        }