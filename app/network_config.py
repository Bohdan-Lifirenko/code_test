from flask import Blueprint, request, redirect, render_template, url_for, current_app

from db_communication import update_servers_config, get_servers_config

network_config_bp = Blueprint('network_config', __name__)

@network_config_bp.route("/network_config", methods=["GET", "POST"])
def network_config():
    if request.method == "POST":
        flask_ip = request.form.get("flask_ip")
        flask_port = int(request.form.get("flask_port"))
        modbus_ip = request.form.get("modbus_ip")
        modbus_port = int(request.form.get("modbus_port"))

        update_servers_config(flask_ip, flask_port, modbus_ip, modbus_port, current_app.config.get("CONFIG_FILE"))
        return redirect(url_for("network_config.network_config"))

    config = get_servers_config(current_app.config.get("CONFIG_FILE"))
    return render_template("network_config.html", config=config)