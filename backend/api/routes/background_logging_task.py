from pathlib import Path
import sys

backend_root = Path(__file__).resolve().parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))


from database.database_config import SessionLocal
import database.models as logging_table


def log_prediction_into_db(product_ids, forcasted_values):
    db = SessionLocal()
    try:
        logs = [
            logging_table.PredictionLog(
                item_id=str(pid),
                prediction_value=float(pred)
            )
            for pid, pred in zip(product_ids, forcasted_values)
        ]

        db.add_all(logs)
        db.commit()

        print("Predictions logged succesfully ✅.")

    except Exception as e:
        print("Error in writing logs to DB.")
        db.rollback()