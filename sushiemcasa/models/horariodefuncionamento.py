from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class HorarioDeFuncionamento(models.Model):
    DAY_CHOICES = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]

    day_of_week = models.IntegerField(
        _("Day of the week"),
        choices=DAY_CHOICES,
        unique=True
    )
    
    is_open = models.BooleanField(
        _("Open?"),
        default=False,
        help_text=_("Check if the store is open on this day.")
    )
    
    open_time = models.TimeField(
        _("Opening time"),
        null=True,
        blank=True,
        help_text=_("Format: HH:MM")
    )
    
    close_time = models.TimeField(
        _("Closing time"),
        null=True,
        blank=True,
        help_text=_("Format: HH:MM")
    )

    class Meta:
        verbose_name = _("Opening hours")
        verbose_name_plural = _("Opening hours")
        ordering = ['day_of_week']

    def __str__(self):
        day_name = self.get_day_of_week_display()
        if self.is_open and self.open_time and self.close_time:
            return f"{day_name}: {self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"
        elif self.is_open:
            return f"{day_name}: Open (hours not set)"
        else:
            return f"{day_name}: Closed"

    def clean(self):
        if self.is_open:
            if not self.open_time or not self.close_time:
                raise ValidationError(
                    _("Opening and closing times are required for an open day.")
                )
            
            if self.close_time <= self.open_time:
                raise ValidationError(
                    _("Closing time must be later than opening time.")
                )
        
        if not self.is_open:
            self.open_time = None
            self.close_time = None