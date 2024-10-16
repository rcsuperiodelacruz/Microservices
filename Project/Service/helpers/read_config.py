import yaml, logging.config, logging


def read_app_config():
    with open('./config/app_conf.yml', 'r') as file:
        app_config = yaml.safe_load(file.read())

    return app_config


def get_config():
    app_config = read_app_config()

    filename = app_config['datastore']['filename']
    seconds = app_config['scheduler']['period_sec']
    url = app_config['eventstore']['url']

    return filename, seconds, url    


def read_log_config():
    with open('./config/log_conf.yml', 'r') as file:
        log_config = yaml.safe_load(file.read())
        logging.config.dictConfig(log_config)

    logger = logging.getLogger('basicLogger')

    return logger

