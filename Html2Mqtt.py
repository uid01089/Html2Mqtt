import logging
import paho.mqtt.client as pahoMqtt
from flask import Flask, request, jsonify, current_app
from flask_apscheduler import APScheduler
from flask_cors import CORS
from PythonLib.Mqtt import MQTTHandler, Mqtt
from PythonLib.Scheduler import Scheduler
from PythonLib.DateUtil import DateTimeUtilities
from PythonLib.JsonUtil import JsonUtil

logger = logging.getLogger('Html2Mqtt')


# https://gunicorn.org/ : gunicorn -w 4 -b 127.0.0.1:8000 your_module:create_app


class Module:
    def __init__(self) -> None:
        self.scheduler = Scheduler()
        self.mqttClient = Mqtt("koserver.iot", "/house/agents/Html2Mqtt", pahoMqtt.Client("Html2Mqtt"))

    def getScheduler(self) -> Scheduler:
        return self.scheduler

    def getMqttClient(self) -> Mqtt:
        return self.mqttClient

    def setup(self) -> None:
        self.scheduler.scheduleEach(self.mqttClient.loop, 500)

    def loop(self) -> None:
        self.scheduler.loop()


class Html2Mqtt:
    def __init__(self, module: Module) -> None:
        self.mqttClient = module.getMqttClient()
        self.scheduler = module.getScheduler()

    def setup(self) -> None:
        self.scheduler.scheduleEach(self.__keepAlive, 10000)

    def __keepAlive(self) -> None:
        self.mqttClient.publishIndependentTopic('/house/agents/Html2Mqtt/heartbeat', DateTimeUtilities.getCurrentDateString())
        self.mqttClient.publishIndependentTopic('/house/agents/Html2Mqtt/subscriptions', JsonUtil.obj2Json(self.mqttClient.getSubscriptionCatalog()))

    def mirrorToMqtt(self, topic: str, value: str) -> None:
        logger.info(f'{topic} - {value}')
        self.mqttClient.publishIndependentTopic(topic, value)


def create_app(*args, **kwargs):
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('Html2Mqtt').setLevel(logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

    flaskApp = Flask(__name__)
    CORS(flaskApp, supports_credentials=True, expose_headers='Access-Control-Allow-Credentials')  # Explicitly set CORS headers

    scheduler = APScheduler()
    scheduler.init_app(flaskApp)

    module = Module()
    module.setup()

    html2Mqtt = Html2Mqtt(module)
    html2Mqtt.setup()
    flaskApp.html2Mqtt = html2Mqtt   # Attach html2Mqtt to current_app

    @scheduler.task('interval', id='your_periodic_function', seconds=0.5)
    def your_periodic_function():
        module.loop()

    @flaskApp.route('/api/store', methods=['POST', 'OPTIONS'])
    def store():

        def sendObj(objToSend: object) -> bool:
            success = True
            try:
                topic = objToSend['topic']
                value = objToSend['value']

                current_app.html2Mqtt.mirrorToMqtt(topic, value)
            except KeyError:
                success = False

            return success

        if request.method == 'OPTIONS':
            # Respond to preflight request
            response = jsonify({'message': 'Preflight request successful'})
            return response

        success = True
        receivedObjects = request.json
        if isinstance(receivedObjects, list):
            for receivedObject in receivedObjects:
                success = success and sendObj(receivedObject)
        else:
            success = success and sendObj(receivedObjects)

        if success:
            return jsonify({'message': 'POST request successful', 'data': request.json})
        else:
            return jsonify(error='Invalid request. Both key and value are required.'), 400

    # Start the scheduler
    scheduler.start()

    return flaskApp


# Entry point for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
