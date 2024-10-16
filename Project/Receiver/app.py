from flask import request
from connexion import NoContent
from requests import post
from helpers.read_config import get_urls, read_log_config
import connexion, uuid


gun_stat_url, item_transaction_url = get_urls()
logger = read_log_config() 


def create_gun_stat(body):
    trace_id = gen_trace_id()
    body['trace_id'] = trace_id

    log_message(trace_id, "create_gun_stat", "receive")

    message = post(gun_stat_url, json=body, headers=request.headers)

    log_message(trace_id, "create_gun_stat", "return", message.status_code)

    return NoContent, message.status_code


def create_purchase_transaction(body):
    trace_id = gen_trace_id()
    body['trace_id'] = trace_id

    log_message(trace_id, "create_purchase_transaction", "receive")

    message = post(item_transaction_url, json=body, headers=request.headers)

    log_message(trace_id, "create_purchase_transaction", "return", message.status_code)

    return NoContent, message.status_code


def gen_trace_id():
    return str(uuid.uuid4())


def log_message(trace_id, event_name, event, status_code=400):
    if event == "receive":
        # Event request receipt log
        logger.info(f"Received event {event_name} request with a trace id of {trace_id}")
    else:
        # Response event log
        logger.info(f"Returned event {event_name} response ID: {trace_id} with status {status_code}")


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("./config/openapi.yml", strict_validation=True, validate_response=True)


if __name__ == "__main__":
    app.run(port=8080)