from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date, time
from sushiemcasa.forms.pedidos import OrderForm
from django.utils import timezone
import datetime

class OrderFormValidationTest(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.tomorrow = self.now + timedelta(days=1)
        self.day_after_tomorrow = self.now + timedelta(days=2)

    def test_valid_delivery_time(self):
        valid_datetime = self.day_after_tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        if valid_datetime.weekday() == 6:
            valid_datetime += timedelta(days=1)

        form_data = {'delivery_datetime': valid_datetime.strftime('%Y-%m-%dT%H:%M')}
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid, but got errors: {form.errors}")

    def test_invalid_delivery_time_too_soon(self):
        soon_time = self.now + timedelta(hours=12)
        form_data = {'delivery_datetime': soon_time.strftime('%Y-%m-%dT%H:%M')}
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_datetime', form.errors)
        self.assertIn("A data de entrega deve ter pelo menos 24 horas de antecedência.", form.errors['delivery_datetime'])

    def test_invalid_delivery_time_in_past(self):
        past_time = self.now - timedelta(days=1)
        form_data = {'delivery_datetime': past_time.strftime('%Y-%m-%dT%H:%M')}
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_datetime', form.errors)
        self.assertIn("A data de entrega deve ter pelo menos 24 horas de antecedência.", form.errors['delivery_datetime'])

    def test_empty_delivery_time_is_valid(self):
        form_data = {'delivery_datetime': ''}
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data.get('delivery_datetime'))

    def test_invalid_delivery_day_sunday(self):
        test_date = self.now + datetime.timedelta(hours=25)
        while test_date.weekday() != 6:
            test_date += timedelta(days=1)
            
        sunday_time = test_date.replace(hour=14, minute=0, second=0, microsecond=0)

        form_data = {'delivery_datetime': sunday_time.strftime('%Y-%m-%dT%H:%M')}
        form = OrderForm(data=form_data)
        
        self.assertFalse(form.is_valid(), f"Formulário deveria ser inválido para Domingo. Data testada: {sunday_time.strftime('%Y-%m-%d %H:%M')}")
        self.assertIn('delivery_datetime', form.errors)
        self.assertIn("Desculpe, não realizamos entregas aos domingos.", form.errors['delivery_datetime'])

    def test_invalid_delivery_time_too_early(self):
        valid_date = self.day_after_tomorrow.date()
        if valid_date.weekday() == 6:
             valid_date += timedelta(days=1)
        
        early_time = timezone.make_aware(datetime.datetime.combine(valid_date, datetime.time(8, 0)))
        form_data = {'delivery_datetime': early_time.strftime('%Y-%m-%dT%H:%M')}
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_datetime', form.errors)
        self.assertIn("Nosso horário de entrega é entre 10:00 e 20:00.", form.errors['delivery_datetime'])

    def test_invalid_delivery_time_too_late(self):
        valid_date = self.day_after_tomorrow.date()
        if valid_date.weekday() == 6:
            valid_date += timedelta(days=1)
        
        late_time = timezone.make_aware(datetime.datetime.combine(valid_date, datetime.time(20, 0)))
        form_data = {'delivery_datetime': late_time.strftime('%Y-%m-%dT%H:%M')}
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_datetime', form.errors)
        self.assertIn("Nosso horário de entrega é entre 10:00 e 20:00.", form.errors['delivery_datetime'])

    def test_invalid_delivery_day_holiday(self):
        target_year = self.now.year
        holiday_date = date(target_year, 12, 25)
        
        holiday_datetime = timezone.make_aware(datetime.datetime.combine(holiday_date, datetime.time(14, 0)))

        if holiday_datetime < (self.now + timedelta(hours=24)):
            holiday_date = date(target_year + 1, 12, 25)
            holiday_datetime = timezone.make_aware(datetime.datetime.combine(holiday_date, datetime.time(14, 0)))

        form_data = {'delivery_datetime': holiday_datetime.strftime('%Y-%m-%dT%H:%M')}
        form = OrderForm(data=form_data)
        
        self.assertFalse(form.is_valid(), f"Form should be invalid for holiday {holiday_date}. Errors: {form.errors}")
        self.assertIn('delivery_datetime', form.errors)
        self.assertIn(f"Não realizamos entregas no dia {holiday_date.strftime('%d/%m/%Y')}.", form.errors['delivery_datetime'])