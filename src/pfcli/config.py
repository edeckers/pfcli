from pfcli.environment import env


APPLICATION_PFSENSE_HOSTNAME = env("PFSENSE_HOSTNAME", "192.168.0.1")
APPLICATION_PFSENSE_USERNAME = env("PFSENSE_USERNAME", "admin")
APPLICATION_PFSENSE_PASSWORD = env("PFSENSE_PASSWORD", "pfsense")
