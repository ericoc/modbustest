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
def api_get_all():
    resp = make_response(jsonify(coils=__discover(app.config["MODBUS_COILS"])))
    resp.headers["Content-type"] = "application/json"
    return resp


@app.route("/api/all/", methods=["POST"])
@app.route("/api/all/<int:value>/", methods=["POST"])
def api_post_all(value: int = None):
    set_coil = None
    if value is not None:
        if value not in (0, 1):
            abort(400)
        set_coil = bool(value)

    for _coil, _existing in __discover().items():
        if set_coil is None:
            value = not _existing
        if value != _existing:
            g.client.write_coil(address=_coil, value=value)

    return api_get_all()


@app.route("/api/<int:coil>/", methods=["GET"])
def api_get_coil(coil: int):

    if isinstance(coil, int):
        if coil not in app.config["MODBUS_COILS"]:
            abort(404)

    resp = make_response(jsonify(coils=__discover([coil])))
    resp.headers["Content-type"] = "application/json"
    return resp


@app.route("/api/<int:coil>/", methods=["POST"])
@app.route("/api/<int:coil>/<int:value>/", methods=["POST"])
def api_post_coil(coil: int, value: int = None):

    if isinstance(coil, int):
        if coil not in app.config["MODBUS_COILS"]:
            abort(404)
    existing = __discover(coils=[coil])

    if value is not None:
        if value not in (0, 1):
            abort(400)
        value = bool(value)

    if value is None:
        value = not existing[coil]

    if value != existing:
        g.client.write_coil(address=coil, value=value)

    resp = make_response(jsonify(coils=__discover([coil])))
    resp.headers["Content-type"] = "application/json"
    return resp


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html.j2", coils=__discover())


@app.teardown_appcontext
def post(err=None):
    if "client" in g:
        g.client.close()
    if err:
        raise err


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
