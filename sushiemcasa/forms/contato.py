from django import forms
from sushiemcasa.models.contato import MensagemFeedback 

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = MensagemFeedback
        fields = ['nome', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'name (optional)'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email (optional)'}),
            'mensagem': forms.Textarea(attrs={'rows': 8, 'placeholder': 'your feedback...'}),
        }