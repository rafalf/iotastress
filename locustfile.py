from locust import HttpUser, TaskSet, User, task, between, events
import yaml
import logging
import logging.config
from log_format import LOGGING_CONFIG
import random
import pprint

import time
import random
import string
import json

import iota_client
import os

ENVIRONMENT = "testnet"


class SendIotas(TaskSet):
    @task
    def send(self):
        self.client.execute('message')


class Locustio(HttpUser):
    tasks = [SendIotas]
    # logging.config.dictConfig(LOGGING_CONFIG)
    # log = logging.getLogger('main')


class Debug(HttpUser):

    def __init__(self, *args, **kwargs):
        super(HttpUser, self).__init__(*args, **kwargs)
        self.client = CustomClient()

    tasks = [SendIotas]

    with open("config.yaml", 'r') as hdlr:
        cf = yaml.load(hdlr, Loader=yaml.FullLoader)
    User.host = cf[ENVIRONMENT]['host']

    logging.config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger('main')


class CustomClient(object):

    def __init__(self):
        #self.node = "http://iotaftrsceao.ddns.net:14265"
        self.node = "https://api.hornet-0.testnet.chrysalis2.com"
        sender_seed = ''
        receiver_seed = ''
        self.address = ''

    def execute(self, command):
        start_time = time.time()

        try:
            if command == 'value':
                pass
            elif command == "message":
                client = iota_client.Client(
                    node=self.node, node_sync_disabled=True, local_pow=False)
                msg = 'PY MESSENGER ' + ''.join(random.choices(
                    string.ascii_uppercase + string.digits, k=30))

                print(f'message() Indexation {msg}')
                message_id_indexation = client.message(
                    index="Hi", data_str=msg)
                # message_id_indexation = client.message(
                #     index="Hello", data=[84, 97, 110, 103, 108, 101])

                print(f'Indexation sent with message_id: {message_id_indexation["message_id"]}')

        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="execute", name=command, response_time=total_time, exception=e)
            print("exception: %s" % str(e))
        else:
            elapsed_time = time.time() - start_time
            total_time = int(elapsed_time * 1000)
            print("Took %s to send %s" % (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)), msg))
            events.request_success.fire(request_type="execute", name=command, response_time=total_time,
                                        response_length=0)


if __name__ == '__main__':
    from locust.env import Environment
    my_env = Environment(user_classes=[Debug])
    Debug(my_env).run()