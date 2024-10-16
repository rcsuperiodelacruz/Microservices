from datetime import datetime, timedelta
from sqlalchemy import func, desc
import requests

from helpers.read_config import get_config
from helpers.log_message import success_response, error_response, log_events

filename, seconds, url = get_config()


def fetch_recent(session, table):
    result = session.query(table).order_by(desc(table.last_updated)).first()

    return result.to_dict()


def row_counter(session, table):
    result = session.query(func.count(table.id)).scalar()

    if result == 0:
        return None
    else:
        return fetch_recent(session, table)


def check_db(session, table):
    result = row_counter(session, table)

    if result is None:
        return {
            "num_gun_stat_events": 0,
            "head_shot_count": 0,
            "bullet_shot_count": 0,
            "num_purchase_history_events": 0,
            "total_revenue": 0,
            "last_updated": datetime.now(),
        }
    else:
        return result
    

def count_sum(count, events, property):
    for event in events:
        count += event[property]

    return count


def update_stats(stats_data, goal_events, boost_events, new_event):
    """Update the stats based on new goal and boost events."""
    last_updated = stats_data['last_updated']

    if len(boost_events) > 0:
        num_boost = stats_data['num_boost_events'] + len(boost_events)
        total_boost_pickups = count_sum(stats_data['total_boost_pickups'], boost_events, "boost_amount")
        avg_boost_per_event = total_boost_pickups / num_boost if num_boost > 0 else 0
        last_updated = datetime.strptime(boost_events[-1]['date_created'], '%Y-%m-%dT%H:%M:%SZ')
    else:
        num_boost = stats_data['num_boost_events']
        total_boost_pickups = stats_data['total_boost_pickups']
        avg_boost_per_event = stats_data['avg_boost_per_event']

    if len(goal_events) > 0:
        num_goal = stats_data['num_goal_events'] + len(goal_events)
        max_goal_speed = max(goal_event['goal_speed'] for goal_event in goal_events)
        last_updated = max(last_updated, datetime.strptime(goal_events[-1]['date_created'], '%Y-%m-%dT%H:%M:%SZ'))
    else:
        num_goal = stats_data['num_goal_events']
        max_goal_speed = stats_data['max_goal_speed']

    # Ensure last_updated is retained if no new events
    if len(goal_events) == 0 and len(boost_events) == 0:
        last_updated = stats_data['last_updated']

    return {
        "num_goal_events": num_goal,
        "max_goal_speed": max_goal_speed,
        "num_boost_events": num_boost,
        "total_boost_pickups": total_boost_pickups,
        "avg_boost_per_event": avg_boost_per_event,
        "last_updated": last_updated,
        "new_event": new_event
    }


def update_storage(logger, stats_data):
    error = False

    params = {
        "start_timestamp": stats_data['last_updated'].strftime('%Y-%m-%dT%H:%M:%SZ'),
        "end_timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    }

    gs_res = requests.get(f"{url}/get/gun_stats", params=params)
    ph_res = requests.get(f"{url}/get/purchase_transactions", params=params)

    if gs_res.status_code != 201:
        error_response(logger, "gs")
        error = True
    
    if ph_res.status_code != 201:
        error_response(logger, "ph")
        error = True

    if error:
        return "error"
    
    gs_events = gs_res.json()
    ph_events = ph_res.json()

    new_event = success_response(logger, len(gs_events), len(ph_events))

    log_events(logger, gs_events, ph_events)

    return update_stats(stats_data, gs_events, ph_events, new_event)
