#!/usr/bin/env python3
from flask import abort, Flask, g, render_template
from pymodbus.client import ModbusTcpClient


app = Flask(__name__)
app.config.from_pyfile("config.py")


@app.before_request
def __pre(host=app.config["MODBUS_HOST"]):
    g.client = ModbusTcpClient(host=host)
    g.client.connect()


def __discover(coils=app.config["MODBUS_COILS"]) -> dict:
    coil_values = {}
    for coil in coils:
        value = g.client.read_coils(address=coil, count=1)
        coil_values[coil] = value.bits[0]
    return coil_values


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html.j2", coils=__discover())


@app.route("/toggle/<int:coil>/<int:value>/", methods=["GET"])
def toggle(coil: int, value: (bool, int)):
    if coil not in __discover():
        abort(404)
    if isinstance(value, int):
        if value not in (0, 1):
            abort(400)
        value = bool(value)
    g.client.write_coil(address=coil, value=value)
    return index()


@app.route("/toggle/all/", methods=["GET"])
def toggle_all():
    for coil, value in __discover().items():
        toggle(coil, not value)
    return index()


@app.teardown_appcontext
def post(err=None):
    if "client" in g:
        g.client.close()
    if err:
        raise err


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
