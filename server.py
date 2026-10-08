import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request


app = Flask(__name__)
DATABASE = Path(__file__).with_name("messages.db")
ALLOWED_ORIGINS = {
    "http://localhost:8000",
    "http://127.0.0.1:8000",
}


def initialize_database():
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                inquiry_type TEXT NOT NULL DEFAULT '',
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Vary"] = "Origin"
    return response


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.route("/contact", methods=["POST", "OPTIONS"])
def contact():
    if request.method == "OPTIONS":
        return "", 204

    if not request.is_json:
        return jsonify(success=False, message="Expected a JSON request."), 415

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify(success=False, message="Expected a JSON object."), 400

    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip()
    inquiry_type = str(payload.get("type", "")).strip()
    message = str(payload.get("message", "")).strip()

    if not name or not email or "@" not in email or not message:
        return jsonify(success=False, message="Enter a name, valid email, and message."), 400

    if len(name) > 200 or len(email) > 320 or len(inquiry_type) > 200 or len(message) > 10000:
        return jsonify(success=False, message="One or more fields are too long."), 400

    try:
        with sqlite3.connect(DATABASE) as connection:
            connection.execute(
                """
                INSERT INTO contact_messages (name, email, inquiry_type, message)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, inquiry_type, message),
            )
    except sqlite3.Error:
        app.logger.exception("Could not save contact message")
        return jsonify(success=False, message="The message could not be saved."), 500

    return jsonify(success=True, message="Your message was received."), 201


initialize_database()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)