import yaml, logging, logging.config


def database_config():
    with open('./config/app_conf.yml', 'r') as file:
        app_config = yaml.safe_load(file.read())

        user = app_config["datastore"]["user"]
        password = app_config["datastore"]["password"]
        hostname = app_config["datastore"]["hostname"]
        port = app_config["datastore"]["port"]
        db = app_config["datastore"]["db"]

    return user, password, hostname, port, db
    

def read_log_config():
    with open('./config/log_conf.yml', 'r') as file:
        log_config = yaml.safe_load(file.read())
        logging.config.dictConfig(log_config)

    logger = logging.getLogger('basicLogger')

    return logger