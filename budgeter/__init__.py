import os
from pathlib import Path
from typing import Optional

from flask import Flask
from ruamel.yaml import YAML


def create_app(*, test_config: Optional[Path] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=Path(os.path.join(app.instance_path, "budgeter.sqlite")),
    )
    yaml = YAML(typ="safe")

    if test_config:
        mapping = yaml.load(Path(test_config))
        app.config.from_mapping(mapping)
    else:
        mapping = yaml.load(Path(os.path.join(Path.cwd(), "budgeter", "config.yaml")))
        app.config.from_mapping(mapping)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"

    from . import db

    db.init_app(app)

    # from . import budget
    # app.register_blueprint(budget.bp)
    # app.add_url_rule('/', endpoint='index')

    return app
