import os

#manufacturer_id = '00000000-0000-0000-0000-000000000000'
PROD_BASE_URL = 'https://api.xtrodes.biot-med.com'
DEV_BASE_URL = 'https://api.dev.xtrodes1.biot-med.com'


ORG_NAME = os.environ['ORG_NAME']
RELEASE_TAG = os.environ['RELEASE_TAG']
ENV = os.environ['ENV']
DEV_PASSWORD = os.environ['DEV_PASSWORD']
DEV_USERNAME = os.environ['DEV_USERNAME']
PROD_PASSWORD = os.environ['PROD_PASSWORD']
PROD_USERNAME = os.environ['PROD_USERNAME']
GITHB_TOKEN = os.environ['GITHB_TOKEN']
USER_AGENT = os.environ['USER_AGENT']