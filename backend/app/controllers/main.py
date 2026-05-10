from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone

bp = Blueprint("main", __name__)


# ---------------------------------------------------------------------------
# CPU-bound helper
# ---------------------------------------------------------------------------

def _cpu_bound_task(value: float) -> float:
    """Repetitive arithmetic to simulate CPU-bound load."""
    result = 0.0
    for i in range(100_000):
        result += value / (i + 1)
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "db_type": current_app.config["DB_TYPE"]})


@bp.route("/api/submit", methods=["POST"])
def submit():
    """Receive form data, run CPU-bound task, persist result to DB."""
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", ""))
    surname = str(data.get("surname", ""))
    code = str(data.get("code", ""))
    description = str(data.get("description", ""))

    try:
        value = float(data.get("value", 1.0))
    except (TypeError, ValueError):
        return jsonify({"error": "Câmpul 'value' trebuie să fie numeric."}), 400

    cpu_result = _cpu_bound_task(value)
    db_type = current_app.config["DB_TYPE"]
    record_id = None

    if db_type == "sql":
        from app import db
        from app.models.sql_model import Record

        record = Record(
            name=name,
            surname=surname,
            code=code,
            value=value,
            description=description,
            result=cpu_result,
        )
        db.session.add(record)
        db.session.commit()
        record_id = record.id
    else:
        mongo_db = current_app.mongo_db
        doc = {
            "name": name,
            "surname": surname,
            "code": code,
            "value": value,
            "description": description,
            "result": cpu_result,
            "created_at": datetime.now(timezone.utc),
        }
        ins = mongo_db.records.insert_one(doc)
        record_id = str(ins.inserted_id)

    return jsonify(
        {
            "status": "success",
            "id": record_id,
            "result": round(cpu_result, 6),
            "db_type": db_type,
        }
    )


@bp.route("/api/benchmark/cpu", methods=["GET"])
def benchmark_cpu():
    """CPU-bound benchmark: 100 000-iteration arithmetic loop."""
    try:
        value = float(request.args.get("value", 42.0))
    except (TypeError, ValueError):
        value = 42.0

    result = _cpu_bound_task(value)
    return jsonify({"status": "ok", "result": round(result, 6)})


@bp.route("/api/benchmark/io", methods=["GET"])
def benchmark_io():
    """I/O-bound benchmark: bulk database insertions."""
    try:
        count = max(1, min(int(request.args.get("count", 10)), 500))
    except (TypeError, ValueError):
        count = 10

    db_type = current_app.config["DB_TYPE"]
    now = datetime.now(timezone.utc)

    if db_type == "sql":
        from app import db
        from app.models.sql_model import Record

        for i in range(count):
            db.session.add(
                Record(
                    name=f"bench_{i}",
                    surname="test",
                    code=f"B{i:05d}",
                    value=float(i),
                    description="benchmark",
                    result=float(i * 2),
                )
            )
        db.session.commit()
    else:
        mongo_db = current_app.mongo_db
        docs = [
            {
                "name": f"bench_{i}",
                "surname": "test",
                "code": f"B{i:05d}",
                "value": float(i),
                "description": "benchmark",
                "result": float(i * 2),
                "created_at": now,
            }
            for i in range(count)
        ]
        mongo_db.records.insert_many(docs)

    return jsonify(
        {"status": "ok", "records_inserted": count, "db_type": db_type}
    )


@bp.route("/api/records", methods=["GET"])
def get_records():
    """Return the 50 most recent records."""
    db_type = current_app.config["DB_TYPE"]

    if db_type == "sql":
        from app.models.sql_model import Record

        records = (
            Record.query.order_by(Record.created_at.desc()).limit(50).all()
        )
        return jsonify([r.to_dict() for r in records])
    else:
        mongo_db = current_app.mongo_db
        rows = list(
            mongo_db.records.find().sort("created_at", -1).limit(50)
        )
        for row in rows:
            row["_id"] = str(row["_id"])
            if isinstance(row.get("created_at"), datetime):
                row["created_at"] = row["created_at"].isoformat()
        return jsonify(rows)
