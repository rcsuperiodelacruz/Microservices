import connexion
from apscheduler.schedulers.background import BackgroundScheduler

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base import Base
from stats import Stats

from helpers.log_message import start_request, end_request, data_found, data_not_found, start_periodic, end_periodic, updated_db, no_events
from helpers.query_database import row_counter, check_db, update_storage
from helpers.read_config import get_config, read_log_config
filename, seconds, url = get_config()    
logger = read_log_config()

DB_ENGINE = create_engine("sqlite:///%s" %filename)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_stats():
    start_request(logger)

    session = DB_SESSION()

    response = row_counter(session, Stats)

    session.close()

    if response == None:
        data_not_found(logger, 400, "No new data")

        return response['message'], response['status_code']
    else:
        data_found(logger, response)
        end_request(logger)

        return response, 200


def populate_stats():
    start_periodic(logger)

    session = DB_SESSION()

    data = check_db(session, Stats)

    new_data = update_storage(logger, data)

    if new_data == "error":
        return

    pr = Stats(
        new_data['num_gun_stat_events'],
        new_data['head_shot_count'],
        new_data['bullet_shot_count'],
        new_data['num_purchase_history_events'],
        new_data['total_revenue'],
        new_data['last_updated'],
    )

    session.add(pr)

    session.commit()
    session.close()

    if new_data['new_event']:
        updated_db(logger, new_data)
    else:
        no_events(logger, new_data['last_updated'])

    end_periodic(logger)
    

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=seconds)

    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("./config/openapi.yml", strict_validation=True, validate_response=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)

