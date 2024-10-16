# get_stats()
# ---------------------------------------------------------------
def start_request(logger):
    logger.info("New request initialized")


def end_request(logger):
    logger.info("New request complete")


def data_found(logger, data):
    num_goal_events = data['num_goal_events']
    max_goal_speed = data['max_goal_speed']
    num_boost_events = data['num_boost_events']
    total_boost_pickups = data['total_boost_pickups']
    avg_boost_per_event = data['avg_boost_per_event']
    last_updated = data['last_updated']

    logger.debug(f"Goal events: {num_goal_events} | Boost events: {num_boost_events} || "
                 f"Max goal speed: {max_goal_speed} km/h || Total boost pickups: {total_boost_pickups} || "
                 f"Average boost per event: {avg_boost_per_event} || Last updated: {last_updated}")


def data_not_found(logger, status_code, message):
    logger.error(f"Status Code: {status_code} - Message: {message}")


# populate_stats()
# ---------------------------------------------------------------
def start_periodic(logger):
    logger.info("Started periodic processing")


def end_periodic(logger):
    logger.info("Ended periodic processing")


def success_response(logger, goal_events, boost_events):
    if goal_events > 0 and boost_events > 0:
        logger.info(f"Received new events - goal_stats: {goal_events} | boost_stats: {boost_events}")
        return True
    elif goal_events > 0 and boost_events == 0:
        logger.info(f"Received new events - goal_stats: {goal_events} | no new boost stats events received")
        return True
    elif goal_events == 0 and boost_events > 0:
        logger.info(f"Received new events - no new goal stat events received | boost_stats: {boost_events}")
        return True
    else:
        logger.info("No new events received")
        return False


def error_response(logger, event_type):
    if event_type == "goal_stats":
        logger.error("There was an unexpected error fetching new events from goal stats API")

    if event_type == "boost_stats":
        logger.error("There was an unexpected error fetching new events from boost stats API")


def log_events(logger, goal_events, boost_events):
    if len(goal_events) > 0:
        for event in goal_events:
            trace_id = event['trace_id']
            logger.debug(f"GoalStat Event: {trace_id}")

    if len(boost_events) > 0:
        for event in boost_events:
            trace_id = event['trace_id']
            logger.debug(f"BoostStat Event: {trace_id}")


def updated_db(logger, data):
    num_goal_events = data['num_goal_events']
    max_goal_speed = data['max_goal_speed']
    num_boost_events = data['num_boost_events']
    total_boost_pickups = data['total_boost_pickups']
    avg_boost_per_event = data['avg_boost_per_event']
    last_updated = data['last_updated']

    logger.debug(f"Event was processed with the updated values: Goal Events: {num_goal_events} | Boost Events: {num_boost_events} || "
                 f"Max Goal Speed: {max_goal_speed} || Total Boost Pickups: {total_boost_pickups} || "
                 f"Average Boost per Event: {avg_boost_per_event} || Last Updated: {last_updated}")


def no_events(logger, last_updated):
    logger.debug(f"There were no new events received. Last Updated: {last_updated}")
