import connexion
from connexion import NoContent
import logging
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
from goal_event import GoalEvent
from boost_event import BoostEvent
from helpers.read_config import database_config, read_log_config
from helpers.get_dates import fetch_timestamp_results
import datetime
user, password, hostname, port, db = database_config()
logger = read_log_config()

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
print("connected to DB")

# fetch functions

# def fetch_goal_info(start_timestamp, end_timestamp):
#     session = DB_SESSION()

#     results = fetch_timestamp_results(start_timestamp, end_timestamp, session, GoalEvent)

#     session.close()

#     log_info("Goal Info", start_timestamp, len(results))

#     return results, 201

def fetch_goal_info(start_timestamp, end_timestamp):
    logger.debug(f"Fetching goal events from {start_timestamp} to {end_timestamp}")
    session = DB_SESSION()

    try:
        # Parse the timestamps
        start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
        end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

        # Query for goal events within the given time range
        results = session.query(GoalEvent).filter(
            and_(GoalEvent.date_created >= start_timestamp_datetime, GoalEvent.date_created < end_timestamp_datetime)
        )
        
        logger.debug(f"Number of results fetched: {results.count()}")

        # Convert results to a list of dictionaries
        results_list = [result.to_dict() for result in results]
        return results_list, 200

    except Exception as e:
        logger.error(f"Error while fetching goal events: {str(e)}")
        return {"message": "An error occurred while fetching goal events."}, 500

    finally:
        session.close()


def fetch_boost_info(start_timestamp, end_timestamp):
    logger.debug(f"Fetching boost events from {start_timestamp} to {end_timestamp}")
    session = DB_SESSION()

    try:
        # Parse the timestamps
        start_timestamp_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
        end_timestamp_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")

        # Query for boost events within the given time range
        results = session.query(BoostEvent).filter(
            and_(BoostEvent.date_created >= start_timestamp_datetime, BoostEvent.date_created < end_timestamp_datetime)
        )
        
        logger.debug(f"Number of results fetched: {results.count()}")

        # Convert results to a list of dictionaries
        results_list = [result.to_dict() for result in results]
        return results_list, 200

    except Exception as e:
        logger.error(f"Error while fetching boost events: {str(e)}")
        return {"message": "An error occurred while fetching boost events."}, 500

    finally:
        session.close()




from datetime import datetime  # Ensure this is at the top of your file

def recordGoalEvent(body):
    logger.debug(f"Received body: {body}")
    session = DB_SESSION()
    
    try:
        gs = GoalEvent(
            trace_id=body['trace_id'],
            player_id=body['playerId'],
            goal_speed=body['goalSpeed'],
            goal_type=body['goalType'],
            goal_distance=body['goalDistance'],
            date_created=datetime.now()
        )
        session.add(gs)
        session.commit()

        response = gs.to_dict()
        log_message("goalevent", body['trace_id'])
        
        session.close()

        return response, 201

    except KeyError as e:
        logger.error(f"Missing key in request body: {str(e)}")
        session.rollback()
        return {"message": f"Missing key: {str(e)}"}, 400
    except Exception as e:
        logger.error(f"Error occurred while recording goal event: {str(e)}")
        session.rollback()
        return {"message": "An internal error occurred."}, 500





def recordBoostEvent(body):
    logger.debug(f"Received body: {body}")
    session = DB_SESSION()
    
    bs = BoostEvent(
        trace_id=body['trace_id'],
        player_id=body['playerId'],
        boost_amount=body['boostAmount'],
        total_boost=body['totalBoost'],
        location=body['location'],
        date_created=datetime.now()
    )
    
    session.add(bs)
    session.commit()

    response = bs.to_dict()
    log_message("boostevent", body['trace_id'])

    session.close()

    return response, 201

# logging functions
def log_message(event_name, trace_id):
    logger.debug(f"Stored event {event_name} request with a trace id of {trace_id}")

def log_info(event_type, start_timestamp, result_len):
    logger.info(f"Query for {event_type} events after {start_timestamp} return {result_len} results")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("config/openapi.yml", strict_validation=True, validate_response=True)
print("api connected")

if __name__ == "__main__":
    app.run(port=8090)
