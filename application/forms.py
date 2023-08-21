from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime
from application.models import CURRENCIES

def date_le_today(form, field):
    if field.data > datetime.now().date():
        raise ValidationError("La fecha debe ser anterior a hoy")

def time_le_now(form, field):
    if field.data > datetime.now().time():
        raise ValidationError("La hora debe ser antes que ahora")
    
def validapwd(form, field):
    if field.data != form.pwd.data:
        raise ValidationError("Las contraseñas no coinciden")
    

class MovementForm(FlaskForm):
    date = DateField("Fecha", validators=[DataRequired("Es necesaria la fecha"), date_le_today])
    time = TimeField("Hora", validators=[DataRequired("Es necesaria la hora"), time_le_now])
    currency_from = SelectField("Divisa", validators=[DataRequired("Divisa obligatoria")], choices=[("EUR", "Euros")])
    amount_from = FloatField("Cantidad", validators=[DataRequired("Debes poner una cantidad")])
    currency_to = SelectField("Divisa", validators=[DataRequired("Divisa obligatoria")], choices=[("EUR",   "Euros"), ("ETH",   "Ethereum"), ("BNB",   "Binance Coin"), ("ADA",   "Cardano"), ("DOT",   "Polkadot"), ("BTC",   "Bitcoin"), ("USDT",  "Tether"), ("XRP",   "Ripple"), ("SOL",   "Solana"), ("MATIC", "Polygon")])
    amount_to = FloatField("Cantidad", validators=[DataRequired("Debes poner una cantidad")])

    submit = SubmitField("Enviar")

    def validate_datetime(self, field):
        if field.data > datetime.now():
            raise ValidationError("Debe ser antes de ahora (like a method)")
        
    def validate_currency(self, currency_from, currency_to):
        if currency_from and currency_to not in CURRENCIES:
            raise ValueError(f"Divisa inválida: por favor escoge entre una de estas {CURRENCIES}")
    
    def validate_amount(self, amount):
        if amount <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        
    
    def validate_balance(self, currency, required_amount):
        balance_currency = sum(
            movement.amount_to - movement.amount_from
            for movement in self.movements
            if movement.currency_to == currency or movement.currency_from == currency
        )
        if balance_currency < required_amount:
            raise ValueError(f"No tienes suficientes {currency} para realizar la operación")

    def validate_purchase(self, form):
        currency_from = form.currency_from.data
        amount_from = form.amount_from.data
        currency_to = form.currency_to.data
        amount_to = form.amount_to.data
        
        self.validate_currency(currency_from)
        self.validate_currency(currency_to)
        self.validate_amount(amount_from)
        self.validate_amount(amount_to)

    def validate_trade(self, form):
        currency_from = form.currency_from.data
        amount_from = form.amount_from.data
        currency_to = form.currency_to.data
        amount_to = form.amount_to.data
        
        self.validate_currency(currency_from)
        self.validate_currency(currency_to)
        self.validate_amount(amount_from)
        self.validate_amount(amount_to)
        self.validate_saldo(currency_from, amount_from)

    def validate_sale(self, form):
        currency_from = form.currency_from.data
        amount_from = form.amount_from.data
        currency_to = form.currency_to.data
        amount_to = form.amount_to.data
        
        self.validate_currency(currency_from)
        self.validate_currency(currency_to)
        self.validate_amount(amount_from)
        self.validate_amount(amount_to)
        self.validate_saldo(currency_from, amount_from)
        
        total_eur_compra = sum(
            movement.amount_to for movement in self.movements if movement.currency_to == "EUR"
        ) - sum(
            movement.amount_from for movement in self.movements if movement.currency_from == "EUR"
        )
        total_eur_venta = sum(
            movement.amount_to for movement in self.movements if movement.currency_to == currency_from
        )
        
        if total_eur_venta > total_eur_compra:
            print("Lo haces bien")
        else:
            print("No es tu día")

