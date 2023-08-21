from application import app
from flask import render_template, request, redirect, flash, url_for
from application.models import Movement, MovementDAO, TransactionValidator, CURRENCIES
from application.forms import MovementForm
import requests

dao = MovementDAO(app.config.get("PATH_SQLITE"))

def get_exchange_rates(base_currency, target_currencies):
    url = f"https://api.exchangeratesapi.io/latest?base={base_currency}&symbols={','.join(target_currencies)}"
    response = requests.get(url)
    data = response.json()
    return data["rates"]

@app.route("/exchange_rates")
def exchange_rates():
    target_currencies = CURRENCIES  # Puedes personalizar esta lista según tus necesidades
    base_currency = "EUR"  # La moneda base para obtener las tasas de cambio
    exchange_rates = get_exchange_rates(base_currency, target_currencies)
    
    return render_template("exchange_rates.html", rates=exchange_rates)

@app.route("/")
def index():
    try:
        movements = dao.get_all()
        return render_template("index.html", the_movements=movements, title="Todos")
    except ValueError as e:
        flash("Algo ha ido mal")
        flash(str(e))
        return render_template("index.html", the_movements=[], title="Todos")


@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    form = MovementForm()  # Asegúrate de usar tu formulario personalizado

    if request.method == "GET":
        # Lógica para configurar valores iniciales en el formulario
        return render_template("purchase.html", form=form)
    
    elif request.method == "POST":
        # Lógica para manejar la solicitud POST del formulario
        try:
            validator = TransactionValidator(dao.get_all())  # Utiliza tu DAO para validar
            validator.validate_purchase(form)

            # Crear un nuevo objeto Movement con los datos del formulario
            movement = Movement(
                form.date.data,  # Actualiza con los nombres de tus campos
                form.time.data,  # Actualiza con los nombres de tus campos
                form.currency_from.data,  # Actualiza con los nombres de tus campos
                form.amount_from.data,  # Actualiza con los nombres de tus campos
                form.currency_to.data,  # Actualiza con los nombres de tus campos
                form.amount_to.data  # Actualiza con los nombres de tus campos
            )

            # Realiza operaciones relacionadas con la transacción (si es necesario)

            # Insertar el movimiento en la base de datos
            dao.insert(movement)

            # Redirigir a otra página después de la transacción exitosa
            flash("Transacción exitosa", "success")
            return redirect(url_for("success_page"))  # Actualiza con la ruta correcta
        
        except ValueError as e:
            # Captura errores de validación y muestra en el formulario
            form.errors["general"] = [str(e)]
            return render_template("purchase.html", form=form)

    return render_template("purchase.html", form=form)

@app.route("/status", methods=['GET', 'POST'])
def exchange():
    return "status"

@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html", methods=['GET', 'POST'])
