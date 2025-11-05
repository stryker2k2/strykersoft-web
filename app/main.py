from flask import Flask, render_template, Blueprint, redirect, url_for, request, flash
import logging, json
from pathlib import Path
from .proxmox import getContainers, createTarget

main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

classes_path = "app/data/classes.json"

@main.route('/')
def index():
    with open(classes_path, 'r') as file:
        data = json.load(file)
    return render_template('index.html', navtab="home", data=data)

@main.route('/machines')
def machines():
    containers = []
    return render_template('machines.html', navtab="machines")

@main.route('/walkthru')
def walkthru():
    return render_template('walkthru.html', navtab="walkthru")

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)