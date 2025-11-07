from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models.horariodefuncionamento import HorarioDeFuncionamento

@receiver(post_migrate)
def create_operating_hours(sender, **kwargs):

    if HorarioDeFuncionamento.objects.exists():
        return

    days = [
        (0, "Segunda-feira"),
        (1, "Terça-feira"),
        (2, "Quarta-feira"),
        (3, "Quinta-feira"),
        (4, "Sexta-feira"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    for day_int, day_name in days:
        HorarioDeFuncionamento.objects.create(day_of_week=day_int, is_open=False)
    
    print("Horários de funcionamento padrão criados.")