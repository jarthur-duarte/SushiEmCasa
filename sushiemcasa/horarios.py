"""Horários de retirada a partir do horário de funcionamento definido no painel (Hours).

O checkout lista os horários com `dias_disponiveis()` e o OrderForm confere a
escolha com `motivo_recusa()`, para que as duas pontas usem a mesma regra.
"""
import datetime

from django.utils import timezone

from sushiemcasa.models.horariodefuncionamento import HorarioDeFuncionamento

ANTECEDENCIA = datetime.timedelta(hours=24)
INTERVALO_MIN = 30
DIAS_A_FRENTE = 14
FORMATO_VALOR = '%Y-%m-%d %H:%M'


def _horarios_da_semana():
    """{dia_da_semana: (abre, fecha)} só para os dias abertos com horário completo."""
    return {
        h.day_of_week: (h.open_time, h.close_time)
        for h in HorarioDeFuncionamento.objects.all()
        if h.is_open and h.open_time and h.close_time and h.open_time < h.close_time
    }


def _rotulo_hora(t):
    return t.strftime('%I:%M %p').lstrip('0')


def resumo_da_semana():
    """Linhas como 'Friday: 10:00 AM – 8:00 PM' para mostrar ao cliente."""
    nomes = dict(HorarioDeFuncionamento.DAY_CHOICES)
    return [
        f'{nomes[dia]}: {_rotulo_hora(abre)} – {_rotulo_hora(fecha)}'
        for dia, (abre, fecha) in sorted(_horarios_da_semana().items())
    ]


def dias_disponiveis(agora=None):
    """Dias dos próximos DIAS_A_FRENTE dias com pelo menos um horário livre.

    Cada horário começa em hora cheia ou meia hora, dentro do expediente
    (o último começa antes do fechamento) e a pelo menos 24h de agora.
    """
    agora = timezone.localtime(agora or timezone.now())
    minimo = agora + ANTECEDENCIA
    semana = _horarios_da_semana()
    tz = timezone.get_current_timezone()
    dias = []

    for n in range(DIAS_A_FRENTE + 1):
        data = agora.date() + datetime.timedelta(days=n)
        if data.weekday() not in semana:
            continue
        abre, fecha = semana[data.weekday()]
        inicio = datetime.datetime.combine(data, abre)
        resto = inicio.minute % INTERVALO_MIN
        if resto or inicio.second:
            inicio = inicio.replace(second=0) + datetime.timedelta(minutes=INTERVALO_MIN - resto)
        fim = datetime.datetime.combine(data, fecha)

        horarios = []
        slot = inicio
        while slot < fim:
            aware = timezone.make_aware(slot, tz)
            if aware >= minimo:
                horarios.append({'valor': slot.strftime(FORMATO_VALOR), 'rotulo': _rotulo_hora(slot.time())})
            slot += datetime.timedelta(minutes=INTERVALO_MIN)

        if horarios:
            dias.append({
                'valor': data.isoformat(),
                'semana': data.strftime('%a'),
                'dia': data.day,
                'mes': data.strftime('%b'),
                'extenso': data.strftime('%A, %B ') + str(data.day),
                'horarios': horarios,
            })
    return dias


def motivo_recusa(entrega, agora=None):
    """Mensagem de erro se `entrega` (datetime aware) não pode ser aceita; senão None."""
    agora = agora or timezone.now()
    if entrega < agora + ANTECEDENCIA:
        return 'Pickup must be scheduled at least 24 hours in advance.'
    local = timezone.localtime(entrega)
    semana = _horarios_da_semana()
    nome = dict(HorarioDeFuncionamento.DAY_CHOICES)[local.weekday()]
    if local.weekday() not in semana:
        return f"Sorry, pickup is not available on {nome}s. Please pick one of the available days."
    abre, fecha = semana[local.weekday()]
    if not (abre <= local.time() < fecha):
        return f'On {nome}s pickup is available between {_rotulo_hora(abre)} and {_rotulo_hora(fecha)}.'
    return None
