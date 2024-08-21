#!/usr/bin/env python3
from flask import (
    abort, Flask, g, jsonify, make_response, render_template, request
)
from pymodbus.client import ModbusTcpClient


# Configure Flask.
app = Flask(__name__)
app.config.from_pyfile("config.py")


@app.before_request
def pre(host: str = app.config["MODBUS_HOST"]):
    """Connect to Modbus host/device (ADAM unit)."""
    g.client = ModbusTcpClient(host=host)
    g.client.connect()


def discover(coils: list = app.config["MODBUS_COILS"]) -> dict:
    """
    Discover/return dictionary of Modbus coil(s) numbers with boolean value.
    for example: {16: False, 17: True, 18: False, 19: True, 20: False, 21: True}
    """
    coil_values = {}
    for number in coils:
        value = g.client.read_coils(address=number, count=1)
        coil_values[number] = value.bits[0]
    return coil_values


@app.route("/api/", methods=["GET"])
@app.route("/api/all/", methods=["GET"])
@app.route("/api/<int:coil>/", methods=["GET"])
@app.route("/api/all/", methods=["POST"])
@app.route("/api/all/<int:value>/", methods=["POST"])
@app.route("/api/<int:coil>/", methods=["POST"])
@app.route("/api/<int:coil>/<int:value>/", methods=["POST"])
def api(coil: int = None, value: int = None):
    """API interaction to GET or POST Modbus coil values."""

    # Target all coils, if one was not specified.
    if coil is None:
        coils = app.config["MODBUS_COILS"]

    # If a specific coil number was given, make sure it exists, and target it.
    elif isinstance(coil, int):
        if coil not in app.config["MODBUS_COILS"]:
            abort(404)
        coils = [coil]

    # Handle POST requests, to set coils.
    if request.method == "POST":

        # By default, assume toggling opposite of current value of the coil(s).
        toggle = True

        # If a 0 (false) or 1 (true) value was given, ensure boolean.
        if value is not None:
            if value not in (0, 1):
                abort(400)
            value = bool(value)
            toggle = False

        # Iterate each coil.
        for number, existing in discover(coils=coils).items():

            # Find opposite of existing value of the coil, when toggling.
            if toggle is True:
                value = not existing

            # Write the coil value, if necessary.
            if value != existing:
                g.client.write_coil(address=number, value=value)

    # Re-read the coil values, and return them as JSON.
    resp = make_response(jsonify(coils=discover(coils)))
    resp.headers["Content-type"] = "application/json"
    return resp


@app.route("/", methods=["GET"])
def index():
    """Main index page."""
    return render_template(
        "index.html.j2",
        coils=discover(),
        MODBUS_HOST=app.config["MODBUS_HOST"]
    )


@app.teardown_appcontext
def post(err=None):
    """Close Modbus connection."""
    if "client" in g:
        g.client.close()
    if err:
        raise err


# Run Flask.
if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
