import requests
from flask import jsonify, current_app
from cloudnotes.config import Config


def register_routes(app):
    @app.route("/")
    def index():
        return jsonify({
            "service": "CloudNotes",
            "description": "A small note-taking application with external weather integration.",
            "endpoints": ["/health", "/weather"]
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "message": "CloudNotes is running."})

    @app.route("/weather")
    def weather():
        try:
            response = requests.get(Config.WEATHER_API_URL, timeout=5)
            response.raise_for_status()
            return jsonify({
                "weather_api": Config.WEATHER_API_URL,
                "status": "ok",
                "upstream_status": response.status_code,
                "payload": response.text.strip()
            })
        except requests.RequestException as exc:
            current_app.logger.error("Weather API request failed: %s", exc)
            return jsonify({
                "weather_api": Config.WEATHER_API_URL,
                "status": "error",
                "error": str(exc)
            }), 502
