import time
from threading import Thread, Event
import responder
from dataclasses import dataclass, asdict
import json
from loguru import logger

from cockpit import Cockpit
from websocketserver import WebsocketServer
from common import GoogleMapLatLng


@dataclass()
class VesselINFO(object):
    lat: float
    lng: float
    spd: float
    hdg: float
    mode: str = 'GPS'


class Main(object):
    def __init__(self, *, latDEG: float, lngDEG: float, spdKMH: float, heading: float):

        # self.latDEG = latDEG
        # self.lngDEG = lngDEG
        self.ws = WebsocketServer(debug=True)
        self.cockpit = Cockpit(latDEG=latDEG, lngDEG=lngDEG, kmH=spdKMH, heading=heading)
        self.mainLoop = Thread(target=self.cruise, daemon=True)
        self.mainLoop.start()

        self.api = responder.API(debug=False,
                                 templates_dir='templates',
                                 static_dir='static')
        self.api.add_route('/', self.top)
        self.api.add_route('/turn', self.turn)
        self.api.add_route('/accel', self.accel)
        self.api.add_route('/ws', self.ws.wsserver, websocket=True)
        self.api.run(address='0.0.0.0', port=80)

    def accel(self, req: responder.Request, res: responder.Response):
        self.cockpit.kmH = int(req.params['value'])

    def turn(self, req: responder.Request, res: responder.Response):
        value = 30
        if req.params['direction'] == 'L':
            value *= -1
        self.cockpit.heading += value

    def top(self, req: responder.Request, res: responder.Response):
        res.content = self.api.template('main.html')

    def cruise(self):
        self.cockpit.start()
        while True:
            try:
                if self.cockpit.GPSready.wait():
                    self.cockpit.GPSready.clear()
                    # print(self.cockpit.location)
                    location = GoogleMapLatLng(
                        lat=self.cockpit.latDEG, lng=self.cockpit.lngDEG,
                        spd=self.cockpit.kmH, hdg=self.cockpit.heading)
                    message = json.dumps(asdict(location))
                    # print(message)
                    self.ws.broadCast(message=message)
            except (KeyboardInterrupt) as e:
                self.cockpit.stop()
                logger.error(e)
                break

        self.cockpit.join()
        # timeKeeper.join()


if __name__ == '__main__':
    def main():
        M = Main(latDEG=35.602119, lngDEG=139.368418, spdKMH=36, heading=60)


    main()
