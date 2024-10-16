from flask import request
from connexion import NoContent
import requests
from requests import post
from helpers.read_config import get_urls, read_log_config
import connexion, uuid
goal_event_url, boost_event_url = get_urls()
logger = read_log_config() 


logger.debug("Attempting to add the API...")

def recordGoalEvent(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    message = post(goal_event_url, json=body, headers=request.headers)

    log_message(trace_id, "goalevent", "receive")
    
    return NoContent, message.status_code



def recordBoostEvent(body):
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id

    log_message(trace_id, "boostevent", "receive")
    message = post(boost_event_url, json=body, headers=request.headers)
    print(message.text)
    log_message(trace_id, "boostevent", "return")

    return NoContent, message.status_code

def log_message(trace_id, event_name, event, status_code=400):
    if event == "receive":
        # Event request receipt log
        logger.info(f"Received event {event_name} request with a trace id of {trace_id}")
    else:
        # Response event log
        logger.info(f"Returned event {event_name} response ID: {trace_id} with status {status_code}")


# Create the application
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("config/openapi.yml", strict_validation=True, validate_responses=True)

logger.debug("API added successfully.")

if __name__ == "__main__":
    app.run(port=8080)


