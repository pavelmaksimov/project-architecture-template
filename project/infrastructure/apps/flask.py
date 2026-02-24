"""
Используется для Телеграм ботов, чтобы запустить ручки для prometheus.
"""

import threading

from flask import Flask, jsonify
from flask import Response
from prometheus_client import generate_latest, REGISTRY, CONTENT_TYPE_LATEST

from project.settings import Constants, Settings

app = Flask(__name__)


@app.route(f"{Constants.API_ROOT_PATH}/health")
def healthcheck():
    return jsonify({"status": "ok"})


@app.route(f"{Constants.API_ROOT_PATH}/prometheus")
def prometheus():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)


def run_api_app():
    thread = threading.Thread(
        target=app.run,
        kwargs={
            "host": "0.0.0.0",  # noqa: S104
            "port": Settings().API_PORT,
            "threaded": True,
            "use_reloader": False,
        },
        daemon=True,
    )
    thread.start()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8080,
        threaded=True,
        use_reloader=True,
    )
