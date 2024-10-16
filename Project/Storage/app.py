import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base import Base
from gun_stats import GunStats
from purchase_history import PurchaseHistory
from helpers.read_config import database_config, read_log_config
from helpers.query_database import fetch_timestamp_results
user, password, hostname, port, db = database_config()
logger = read_log_config()

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def fetch_gun_stat(start_timestamp, end_timestamp):
    session = DB_SESSION()

    results = fetch_timestamp_results(start_timestamp, end_timestamp, session, GunStats)

    session.close()

    log_info("Gun Statistics", start_timestamp, len(results))

    return results, 201


def fetch_purchase_transaction(start_timestamp, end_timestamp):
    logger.info("endpoint hit")

    session = DB_SESSION()

    results = fetch_timestamp_results(start_timestamp, end_timestamp, session, PurchaseHistory)

    session.close()

    log_info("Purchase History", start_timestamp, len(results))

    return results, 201


def create_gun_stat(body):
    session = DB_SESSION()

    gs = GunStats(
        body['trace_id'],
        body['gun_id'],
        body['game_id'],
        body['user_id'],
        body['num_bullets_shot'],
        body['num_body_shots'],
        body['num_head_shots'],
        body['num_missed_shots']
    )

    session.add(gs)

    session.commit()
    session.close()

    log_debug("create_gun_stat", body['trace_id'])

    return NoContent, 201


def create_purchase_transaction(body):
    session = DB_SESSION()

    pr = PurchaseHistory(
        body['trace_id'],
        body['transaction_id'],
        body['item_id'],
        body['user_id'],
        body['item_price'],
        body['transaction_date']
    )

    session.add(pr)

    session.commit()
    session.close()

    log_debug("create_purchase_transaction", body['trace_id'])

    return NoContent, 201


def log_debug(event_name, trace_id):
    logger.debug(f"Stored event {event_name} request with a trace id of {trace_id}")


def log_info(event_type, start_timestamp, result_len):
    logger.info(f"Query for {event_type} events after {start_timestamp} return {result_len} results")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("./config/openapi.yml", strict_validation=True, validate_response=True)

if __name__ == "__main__":
    app.run(port=8090)

