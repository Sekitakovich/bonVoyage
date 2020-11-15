import time
from threading import Thread, Event
import responder
from loguru import logger

from cockpit import Cockpit



class Main(object):
    def __init__(self, *, latDEG: float, lngDEG: float, spdKMH: float, heading: float):
        self.cockpit = Cockpit(latDEG=latDEG, lngDEG=lngDEG, kmH=spdKMH, heading=heading)

        self.api = responder.API()
        self.api.add_route('/', self.top)
        self.api.run(address='0,0,0,0', port=80)

    def top(self, req: responder.Request, res: responder.Response):
        res.content = self.api.template('main.html')

    def cruise(self):
        heartBeat = Event()
        def tick():
            while True:
                heartBeat.set()
                time.sleep(1)

        timeKeeper = Thread(target=tick, daemon=True)
        timeKeeper.start()
        while True:
            try:
                if heartBeat.wait():
                    heartBeat.clear()
                    ooo = self.cockpit.current()
                    print(ooo)
            except (KeyboardInterrupt) as e:
                logger.error(e)
                break
        timeKeeper.join()


if __name__ == '__main__':
    def main():
        M = Main(latDEG= 35.602119, lngDEG= 139.368418, spdKMH= 40, heading = 120)
        M.cruise()
        time.sleep(60)
        # for a in range(10):
        #     time.sleep(1)
        #     ooo = M.cockpit.current()
        #     print(ooo)


    main()
