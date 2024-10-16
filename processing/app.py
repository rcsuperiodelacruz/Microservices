import connexion
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from helpers.log_messages import start_request, end_request, data_found, data_not_found, start_periodic, end_periodic, updated_db
from helpers.read_config import get_config, read_log_config
import datetime
from datetime import datetime
import requests
from flask import jsonify


filename, seconds, url = get_config()
logger = read_log_config()
current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def read_stats():
    """Reads stats from the JSON file, creates and returns default if not found."""
    default_stats = {
        "num_goal_events": 0,
        "max_goal_speed": 0.0,
        "num_boost_events": 0,
        "total_boost_pickups": 0,
        "avg_boost_per_event": 0.0,
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }

    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(default_stats, f, indent=4)
        return default_stats
    else:
        with open(filename, 'r') as f:
            return json.load(f)

def write_stats(stats):
    """Writes the stats back to the JSON file."""
    with open(filename, 'w') as f:
        json.dump(stats, f, indent=4)

def get_stats():
    """Fetch the latest stats."""
    start_request(logger)

    response = read_stats()

    if response is None or response == {}:
        data_not_found(logger, 400, "No new data")
        return {"message": "No new data"}, 400
    else:
        data_found(logger, response)
        end_request(logger)
        return response, 200


def populate_stats():
    start_periodic(logger) 
    stats, _ = get_stats()
    start_timestamp = stats["last_updated"]
    end_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Fetch goal events
    goal_responses = requests.get(f"{url}/get/goal", params={"start_timestamp": start_timestamp, "end_timestamp": end_timestamp})
    if goal_responses.status_code == 200:
        goal_events = goal_responses.json()
        logger.info(f"Number of goal events received: {len(goal_events)}")
    else:
        logger.error(f"Error fetching goal events: {goal_responses.status_code} - {goal_responses.text}")
        return  # Early return on error

    # Fetch boost events
    boost_responses = requests.get(f"{url}/get/boost", params={"start_timestamp": start_timestamp, "end_timestamp": end_timestamp})
    if boost_responses.status_code == 200:
        boost_events = boost_responses.json()
        logger.info(f"Number of boost events received: {len(boost_events)}")
    else:
        logger.error(f"Error fetching boost events: {boost_responses.status_code} - {boost_responses.text}")
        return  # Early return on error

    # Continue processing the events
    # (stats update logic goes here)


    # Continue with processing the stats...
    stats["num_goal_events"] += len(goal_events)
    stats["num_boost_events"] += len(boost_events)
    for event in goal_events:
        if float(event["goal_speed"]) > float(stats["max_goal_speed"]):
            stats["max_goal_speed"] = event["goal_speed"]

    total_boost = 0

    for event in boost_events:

        total_boost += event["boost_amount"]
    stats["total_boost_pickups"] += total_boost

    if len(boost_events) > 0:
        stats["total_boost_pickups"] += total_boost
        stats["avg_boost_per_event"] = total_boost / stats["num_boost_events"] if stats["num_boost_events"] > 0 else 0
    stats["last_updated"] = end_timestamp
    print(stats)
    write_stats(stats)

    logger.debug(f"Updated stats: {stats}")
    updated_db(logger, stats) 
    end_periodic(logger)


    if goal_responses.status_code == 200:
        goal_events = goal_responses.json()
        logger.info(f"Number of goal events received: {len(goal_events)}")
    else:
        logger.error(f"Error fetching goal events: {goal_responses.status_code} - {goal_responses.text}")
        return


def init_scheduler():
    """Initialize the background scheduler to run periodic tasks."""
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=seconds)
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("./config/openapi.yml", strict_validation=True, validate_response=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
