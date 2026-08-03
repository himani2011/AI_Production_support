from flask import Blueprint

api = Blueprint("api", __name__)


@api.route("/")
def home():
    return "AI Production Support Assistant"


@api.route("/health")
def health():
    return {
        "status": "Application Running"
    }