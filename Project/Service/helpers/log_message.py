# get_stats()
# ---------------------------------------------------------------
def start_request(logger):
    logger.info("New request initialized")


def end_request(logger):
    logger.info("New request complete")


def data_found(logger, data):
    num_gun_stat_events = data['num_gun_stat_events']
    head_shot_count = data['head_shot_count']
    bullet_shot_count = data['bullet_shot_count']
    num_purchase_history_events = data['num_purchase_history_events']
    item_revenue = data['total_revenue']
    last_updated = data['last_updated']

    logger.debug(f"events: {num_gun_stat_events} | {num_purchase_history_events} || item revenue: {item_revenue} || shots: {bullet_shot_count} | {head_shot_count} || updated: {last_updated}")


def data_not_found(logger, status_code, message):
    logger.error(f"Status Code: {status_code} - Message: {message}")


# populate_stats()
# ---------------------------------------------------------------
def start_periodic(logger):
    logger.info("Started periodic processing")


def end_periodic(logger):
    logger.info("Ended periodic processing")


def success_response(logger, gs_events, ph_events):
    if gs_events > 0 and ph_events > 0:
        logger.info(f"Received new events - gun_stats: {gs_events} | purchase_history: {ph_events}")
        return True
    elif gs_events > 0 and ph_events == 0:
        logger.info(f"Received new events - gun_stats: {gs_events} | no new purchase history events received")
        return True
    elif gs_events == 0 and ph_events > 0:
        logger.info(f"Received new events - no new gun stat events received | purchase_history: {ph_events}")
        return True
    else:
        logger.info("No new events received")
        return False
    

def error_response(logger, event_type):
    if event_type == "gs":
        logger.error("There was an unexpected error fetching new events from gun stats API")

    if event_type == "ph":
        logger.error("There was an unexpected error fetching new events from purchase history API")


def log_events(logger, gs_events, ph_events):
    if len(gs_events) > 0:
        for event in gs_events:
            trace_id = event['trace_id']
            
            logger.debug(f"GunStat Event: {trace_id}")

    if len(ph_events) > 0:
        for event in ph_events:
            trace_id = event['trace_id']

            logger.debug(f"PurchaseHistory Event: {trace_id}")


def updated_db(logger, data):
    num_purchase_history_events = data['num_purchase_history_events']
    num_gun_stat_events = data['num_gun_stat_events']
    total_revenue = data['total_revenue']
    head_shot_count = data['head_shot_count']
    bullet_shot_count = data['bullet_shot_count']
    last_updated = data['last_updated']

    logger.debug(f"Event was processed with the updated values: {num_purchase_history_events} | {num_gun_stat_events} | {total_revenue} | {head_shot_count} | {bullet_shot_count} | {last_updated}")


def no_events(logger, last_updated):
    logger.debug(f"There were no new events received. Last Updated: {last_updated}")

