#!/usr/bin/env python3
from flask import Flask, render_template
from pymodbus.client import ModbusTcpClient


app = Flask(__name__)
app.config.from_pyfile("config.py")


@app.route("/", methods=["GET"])
def index():
    client = ModbusTcpClient(host="adam.home.ericoc.com")
    client.connect()
    coils = {}
    for coil in range(16, 22):
        value = client.read_coils(address=coil, count=1)
        coils[coil] = value.bits[0]
    client.close()
    return render_template("index.html.j2", coils=coils)


if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'])
