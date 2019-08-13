#!/usr/bin/env python3
"""bmarks, bookmarking app"""


from flask import Flask


def create_app():
    """app factory"""

    app = Flask(__name__)

    from . import controller
    app.register_blueprint(controller.blueprint, url_prefix='/')

    return app
