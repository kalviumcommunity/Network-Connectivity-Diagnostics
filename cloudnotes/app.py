from flask import Flask
from cloudnotes.routes import register_routes
from cloudnotes.config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)
register_routes(app)

logging.basicConfig(
    filename="logs/cloudnotes.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("cloudnotes")

@app.before_request
def log_request():
    logger.info("Incoming request: %s %s", __import__("flask").request.method, __import__("flask").request.path)

if __name__ == "__main__":
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=False)
