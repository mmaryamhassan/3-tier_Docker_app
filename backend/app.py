import os
import time

import psycopg2
from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("POSTGRES_HOST", "db"),
    "port": os.environ.get("POSTGRES_PORT", "5432"),
    "dbname": os.environ.get("POSTGRES_DB", "appdb"),
    "user": os.environ.get("POSTGRES_USER", "appuser"),
    "password": os.environ.get("POSTGRES_PASSWORD", "apppass"),
    "sslmode": os.environ.get("POSTGRES_SSLMODE", "prefer"),
}


def get_conn():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        sslmode=DB_CONFIG["sslmode"],
        connect_timeout=5,
    )


def init_db():
    """Create the items table, retrying until the database is reachable."""
    for _ in range(30):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            cur.close()
            conn.close()
            app.logger.info("Database initialized")
            return
        except Exception as exc:  # noqa: BLE001
            app.logger.warning("Database not ready yet: %s", exc)
            time.sleep(2)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/items", methods=["GET"])
def list_items():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, name, description, created_at FROM items ORDER BY id DESC"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"error": "name is required"}), 400
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO items (name, description) VALUES (%s, %s) "
        "RETURNING id, name, description, created_at",
        (name, description),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(dict(row)), 201


@app.route("/api/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"error": "name is required"}), 400
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "UPDATE items SET name=%s, description=%s WHERE id=%s "
        "RETURNING id, name, description, created_at",
        (name, description, item_id),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row is None:
        return jsonify({"error": "item not found"}), 404
    return jsonify(dict(row)), 200


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=%s RETURNING id", (item_id,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if row is None:
        return jsonify({"error": "item not found"}), 404
    return jsonify({"deleted": item_id}), 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
