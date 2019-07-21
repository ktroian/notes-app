#!/bin/sh

. venv/bin/activate
export FLASK_APP=app
export FLASK_DEBUG=1
flask db upgrade
flask run

