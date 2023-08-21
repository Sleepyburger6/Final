from application import app
from datetime import datetime
import sqlite3 as sql
import os
import requests

CURRENCIES = ("EUR", "ETH", "BNB", "ADA", "DOT", "BTC", "USDT", "XRP", "SOL", "MATIC")

class Movement:
    def __init__(self, currency_from, amount_from, currency_to, amount_to, id=None, date=None, time=None):
        self.id = id
        self.currency_from = currency_from
        self.amount_from = amount_from
        self.currency_to = currency_to
        self.amount_to = amount_to
        self.current_date = date or datetime.now().date().strftime("%Y-%m-%d")
        self.current_time = time or datetime.now().time().strftime("%H:%M:%S")

    def validate_currency(self, value):
        if value not in CURRENCIES:
            raise ValueError(f"Debes elegir una de las siguientes divisas {CURRENCIES}")

    def validate_amount(self, value):
        if float(value) <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

    @property
    def currency_from(self):
        return self._currency_from

    @currency_from.setter
    def currency_from(self, value):
        self.validate_currency(value)
        self._currency_from = value

    @property
    def amount_from(self):
        return self._amount_from

    @amount_from.setter
    def amount_from(self, value):
        self.validate_amount(value)
        self._amount_from = float(value)

    @property
    def currency_to(self):
        return self._currency_to

    @currency_to.setter
    def currency_to(self, value):
        self.validate_currency(value)
        self._currency_to = value

    @property
    def amount_to(self):
        return self._amount_to

    @amount_to.setter
    def amount_to(self, value):
        self.validate_amount(value)
        self._amount_to = float(value)

    def __eq__(self, other):
        return (
            self.current_date == other.current_date and
            self.current_time == other.current_time and
            self.currency_from == other.currency_from and
            self.amount_from == other.amount_from and
            self.currency_to == other.currency_to and
            self.amount_to == other.amount_to
        )

    def __repr__(self):
        return (
            f"Movement: {self.current_date} - {self.current_time} - "
            f"{self.currency_from} - {self.amount_from} - "
            f"{self.currency_to} - {self.amount_to}"
        )
    
class MovementDAO:
    def __init__(self, db_path):
        self.path = db_path
        if not os.path.exists(self.path):

            query = """
            CREATE TABLE IF NOT EXISTS "MOVIMIENTOS" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "date" TEXT NOT NULL,
                "time" TEXT NOT NULL,
                "currency_from" TEXT NOT NULL,
                "amount_from" REAL NOT NULL,
                "currency_to" TEXT NOT NULL,
                "amount_to" REAL NOT NULL
            );
            """

            connection = sql.connect(self.path)
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            connection.close()
        

    def insert(self, movements):

        query = """
        INSERT INTO MOVIMIENTOS
            (date, time, currency_from, amount_from, currency_to, amount_to)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        connection = sql.connect(self.path)
        cursor = connection.cursor()
        cursor.execute(query, (movements.current_date, movements.current_time,
                                        movements.currency_from, movements.amount_from, movements.currency_to, movements.amount_to))
        connection.commit()
        connection.close()


    def get(self, id):

        query = """
        SELECT id, date, time, currency_from, amount_from, currency_to, amount_to FROM MOVIMIENTOS WHERE id = ?;
        """

        connection = sql.connect(self.path)
        cursor = connection.cursor()
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        connection.close()
        if result:
            return Movement(*result)
        
    def get_all(self):

        query = """
        SELECT id, date, time, currency_from, amount_from, currency_to, amount_to FROM MOVIMIENTOS ORDER by date;
"""
        connection = sql.connect(self.path)
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        """
        lista = []
        for reg in result:
            lista.append(Movement(*reg))
        """

        lista = [Movement(*reg) for reg in result]

        connection.close()
        return lista
    
class TransactionValidator:
    def __init__(self, movements):
        self.movements = movements

    def validate_currency(self, currency):
        if currency not in CURRENCIES:
            raise ValueError(f"Moneda inválida: por favor escoge entre una de estas{CURRENCIES}")

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

    def validate_purchase(self, currency_from, amount_from, currency_to, amount_to):
        self.validate_currency(currency_from)
        self.validate_currency(currency_to)
        self.validate_amount(amount_from)
        self.validate_amount(amount_to)

    def validate_sale(self, currency_from, amount_from, currency_to, amount_to):
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


import requests

class Exchange:
    def __init__(self, amount, coin_from, coin_to, api_key):
        self.api_key = api_key
        self.amount_to = self.calculate_amount_to(amount, coin_from, coin_to)

    def calculate_amount_to(self, amount, cfrom, cto):
        rate = self.get_exchange_rate(cfrom, cto)
        if rate is not None:
            return amount * rate
        else:
            raise ValueError("No se puede ver el valor seleccionado, prueba más tarde.")

    def get_exchange_rate(self, cfrom, cto):
        url = f"https://rest.coinapi.io/v1/exchangerate/{cfrom}/{cto}"
        headers = {'X-CoinAPI-Key': self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()

            if response.status_code == 200:
                return data.get("rate")
            else:
                return None
            
        except requests.exceptions.RequestException as e:
            return None
