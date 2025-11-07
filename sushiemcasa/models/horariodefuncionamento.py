from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class HorarioDeFuncionamento(models.Model):
    DAY_CHOICES = [
        (0, _('Segunda-feira')),
        (1, _('Terça-feira')),
        (2, _('Quarta-feira')),
        (3, _('Quinta-feira')),
        (4, _('Sexta-feira')),
        (5, _('Sábado')),
        (6, _('Domingo')),
    ]

    day_of_week = models.IntegerField(
        _("Dia da semana"),
        choices=DAY_CHOICES,
        unique=True
    )
    
    is_open = models.BooleanField(
        _("Aberto?"),
        default=False,
        help_text=_("Marque se a loja está aberta neste dia.")
    )
    
    open_time = models.TimeField(
        _("Horário de Abertura"),
        null=True,
        blank=True,
        help_text=_("Formato: HH:MM")
    )
    
    close_time = models.TimeField(
        _("Horário de Fechamento"),
        null=True,
        blank=True,
        help_text=_("Formato: HH:MM")
    )

    class Meta:
        verbose_name = _("Horário de Funcionamento")
        verbose_name_plural = _("Horários de Funcionamento")
        ordering = ['day_of_week']

    def __str__(self):
        day_name = self.get_day_of_week_display()
        if self.is_open and self.open_time and self.close_time:
            return f"{day_name}: {self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"
        elif self.is_open:
            return f"{day_name}: Aberto (Horário pendente)"
        else:
            return f"{day_name}: Fechado"

    def clean(self):
        if self.is_open:
            if not self.open_time or not self.close_time:
                raise ValidationError(
                    _("Para um dia 'Aberto', os horários de abertura e fechamento são obrigatórios.")
                )
            
            if self.close_time <= self.open_time:
                raise ValidationError(
                    _("O horário de fechamento não pode ser anterior ou igual ao de abertura.")
                )
        
        if not self.is_open:
            self.open_time = None
            self.close_time = None