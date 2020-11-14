import time
from threading import Thread

from cockpit import Cockpit
from common import WebServer


class Main(object):
    def __init__(self, *, latDEG: float, lngDEG: float, spdKMH: float, heading: float):
        self.cockpit = Cockpit(latDEG=latDEG, lngDEG=lngDEG, kmH=spdKMH, heading=heading)
        self.cruising = Thread(target=self.cruise, daemon=True)
        self.cruising.start()

    def cruise(self):
        while True:
            ooo = self.cockpit.current()
            print(ooo)
            time.sleep(1)


if __name__ == '__main__':
    def main():
        M = Main(latDEG= 35.602119, lngDEG= 139.368418, spdKMH= 40, heading = 120)
        time.sleep(60)
        # for a in range(10):
        #     time.sleep(1)
        #     ooo = M.cockpit.current()
        #     print(ooo)


    main()
