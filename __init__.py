#!/usr/bin/env python3
from flask import (
    abort, Flask, g, jsonify, make_response, render_template, request
)
from pymodbus.client import ModbusTcpClient


app = Flask(__name__)
app.config.from_pyfile("config.py")


@app.before_request
def __pre(host: str = app.config["MODBUS_HOST"]):
    g.client = ModbusTcpClient(host=host)
    g.client.connect()


def __discover(coils: list = app.config["MODBUS_COILS"]) -> dict:
    coil_values = {}
    for coil in coils:
        value = g.client.read_coils(address=coil, count=1)
        coil_values[coil] = value.bits[0]
    return coil_values


@app.route("/api/", methods=["GET"])
@app.route("/api/all/", methods=["GET"])
@app.route("/api/<int:coil>/", methods=["GET"])
@app.route("/api/all/", methods=["POST"])
@app.route("/api/<int:coil>/", methods=["POST"])
@app.route("/api/all/<int:value>/", methods=["POST"])
@app.route("/api/<int:coil>/<int:value>/", methods=["POST"])
def api(coil: int = app.config["MODBUS_COILS"], value: int = None):

    _status = 200
    __coils = []

    if isinstance(coil, int):
        if coil not in app.config["MODBUS_COILS"]:
            abort(404)
        __coils = [coil]

    if not __coils:
        __coils = app.config["MODBUS_COILS"]

    if request.method == "POST":

        if value is not None:
            if value not in (0, 1):
                abort(400)
            value = bool(value)

        _status = 201
        for _coil, _existing in __discover(coils=__coils).items():
            if value is None:
                value = not _existing
            if value != _existing:
                g.client.write_coil(address=_coil, value=value)
                _status = 202

    resp = make_response(
        jsonify( coils=__discover(coils=__coils), status=_status),
        _status
    )
    resp.headers["Content-type"] = "application/json"
    return resp


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html.j2", coils=__discover())


@app.route("/toggle/<int:coil>/", methods=["GET"])
@app.route("/toggle/<int:coil>/<int:value>/", methods=["GET"])
def toggle(coil: int, value: (bool, int, None) = None):
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
