from datetime import datetime as dt
from dataclasses import dataclass
from operator import xor
from functools import reduce
import math
from loguru import logger

'''
$GPGGA,085120.307,3541.1493,N,13945.3994,E,1,08,1.0,6.9,M,35.9,M,,0000*5E
$GPRMC,085120.307,A,3541.1493,N,13945.3994,E,000.0,240.3,181211,,,A*6A
$GPGLL,3421.7686,N,13222.3345,E,073132,A,A*49
$GPZDA,082220.00,09,01,2006,00,00*60
'''


@dataclass()
class LatLng(object):
    lat: float = 0.0
    lng: float = 0.0


class GhostShip(object):
    def __init__(self, *, lat: float = 35.554315, lng: float = 139.421254, spd: float = 20, hdg: int = 0):
        self.location = LatLng(lat=self.GoogleMaptoGPS(val=lat), lng=self.GoogleMaptoGPS(val=lng))
        self.spd = spd  # kmH
        self.hdg = hdg  # 0 < 360
        self.at = dt.utcnow()
        self.ymdFormat = '%d%m%y'
        self.hmsFormatN = '%H%M%S'
        self.hmsFormatP = '%H%M%S.%f'

        self.isValid = 'A'
        self.ns = 'N'
        self.ew = 'E'
        self.md = 7.0  # 時期偏差

        self.offsetT = 0
        self.offsetM = 0

        self.statD = 2  # 2 = DGPS
        self.ss = 5  # 捕捉している衛星の数
        self.dop = 2.5  # DOP
        self.acc = 3.0
        self.letterA = 'M'
        self.height = 3.5
        self.letterH = 'M'
        self.passed = 0
        self.dgps = 777
        self.statS = 'D'

        self.debug = True

    def GoogleMaptoGPS(self, *, val: float) -> float:  # GoogleMaps -> GPGGA

        decimal, integer = math.modf(val)
        value: float = (integer + ((decimal * 60) / 100)) * 100
        return value

    def meter2mile(self, *, meter: float) -> float:
        return meter / 1852

    def mile2meter(self, *, mile: float) -> float:
        return mile * 1852

    def setSPD(self, *, spd: float):
        self.spd = spd

    def setHDG(self, *, hdg: int):
        self.hdg = hdg

    def getSPD(self) -> float:
        return self.spd

    def getHDG(self) -> int:
        return self.hdg

    def toNMEA(self, *, src: list) -> bytes:
        body = ','.join([str(item) for item in src]).encode()
        csum = ('%02X' % reduce(xor, body, 0)).encode()
        nmea = b'$' + body + b'*' + csum + b'\r\n'
        return nmea

    def GGA(self) -> bytes:
        item = ['GPGGA', self.at.strftime(self.hmsFormatP)[:-3],
                round(self.location.lat, 4), self.ns, round(self.location.lng, 4), self.ew,
                self.statD, self.ss, self.dop, self.acc, self.letterA, self.height, self.letterH, self.passed,
                self.dgps]
        return self.toNMEA(src=item)

    def GLL(self) -> bytes:
        item = ['GPGLL',
                round(self.location.lat, 4), self.ns, round(self.location.lng, 4), self.ew,
                self.at.strftime(self.hmsFormatP)[:-3], self.isValid, self.statS]
        return self.toNMEA(src=item)

    def RMC(self) -> bytes:
        item = ['GPRMC', self.at.strftime(self.hmsFormatP)[:-3], self.isValid,
                round(self.location.lat, 4), self.ns, round(self.location.lng, 4), self.ew,
                self.spd, self.hdg, self.at.strftime(self.ymdFormat), self.md, self.ew, self.statS]
        return self.toNMEA(src=item)

    def ZDA(self) -> bytes:
        item = ['GPZDA',
                self.at.strftime(self.hmsFormatP)[:-3],
                self.at.strftime('%d'), self.at.strftime('%m'), self.at.strftime('%Y'),
                self.offsetT, self.offsetM]
        return self.toNMEA(src=item)

    def move(self):
        now = dt.utcnow()
        secs = (now - self.at).total_seconds()
        head = math.radians((self.hdg * -1) + 90)
        d = (self.spd * secs) / 3600  # Distance in km
        lat = self.location.lat + math.sin(head) * d
        lng = self.location.lng + math.cos(head) * d

        if self.debug:
            logger.debug(f'moved {d:.4f} {lat:.4f}:{lng:.4f} -> {self.location}')

        self.location.lat = lat
        self.location.lng = lng
        self.at = now
        return

    def current(self) -> list:
        self.move()
        result = [self.GGA(), self.GLL(), self.RMC(), self.ZDA()]
        return result


import time

if __name__ == '__main__':
    def main():
        G = GhostShip()

        for loop in range(10):
            time.sleep(1)
            ooo = G.current()
            for nmea in ooo:
                print(nmea)
            print()


    main()
