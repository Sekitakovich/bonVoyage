from dataclasses import dataclass
from datetime import datetime as dt
import math
import time
from operator import xor
from functools import reduce
from threading import Thread, Lock, Event
from loguru import logger

from common import GPSSensor, Constatnts

'''
$GPGGA,085120.307,3541.1493,N,13945.3994,E,1,08,1.0,6.9,M,35.9,M,,0000*5E
$GPRMC,085120.307,A,3541.1493,N,13945.3994,E,000.0,240.3,181211,,,A*6A
$GPGLL,3421.7686,N,13222.3345,E,073132,A,A*49
$GPZDA,082220.00,09,01,2006,00,00*60
'''


class Cockpit(Thread):
    def __init__(self, *, latDEG: float = 0, lngDEG: float = 0, kmH: float = 0, heading: float = 0):
        '''
        内部では緯度経度をDegree形式(GoogleMap)で保持する
        :param latDEG:
        :param lngDEG:
        :param kmH:
        :param heading:
        '''
        super().__init__()
        self.daemon = True

        self.latDEG = latDEG
        self.lngDEG = lngDEG
        self.kmH = kmH
        self.heading = heading

        self.meterPerAngle = 111.111  # この辺アバウトだがしょせん距離数十m/秒程度の移動でしかないので○

        self.utc = dt.utcnow()
        self.ymdFormat = '%d%m%y'
        # self.hmsFormatN = '%H%M%S'
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

        self.locker = Lock()
        self.location = GPSSensor()
        self.GPSready = Event()
        self.running = True

    def toNMEA(self, *, src: list) -> bytes:
        body = ','.join([str(item) for item in src]).encode()
        csum = ('%02X' % reduce(xor, body, 0)).encode()
        nmea = b'$' + body + b'*' + csum + b'\r\n'
        return nmea

    def GGA(self) -> bytes:
        item = ['GPGGA',
                self.utc.strftime(self.hmsFormatP)[:-3],
                round(self.DEGtoDMM(val=self.latDEG), 4), self.ns,
                round(self.DEGtoDMM(val=self.lngDEG), 4), self.ew,
                self.statD, self.ss, self.dop, self.acc, self.letterA, self.height,
                self.letterH, self.passed, self.dgps]
        return self.toNMEA(src=item)

    def GLL(self) -> bytes:
        item = ['GPGLL',
                round(self.DEGtoDMM(val=self.latDEG), 4), self.ns,
                round(self.DEGtoDMM(val=self.lngDEG), 4), self.ew,
                self.utc.strftime(self.hmsFormatP)[:-3], self.isValid, self.statS]
        return self.toNMEA(src=item)

    def RMC(self) -> bytes:
        item = ['GPRMC',
                self.utc.strftime(self.hmsFormatP)[:-3],
                self.isValid,
                round(self.DEGtoDMM(val=self.latDEG), 4), self.ns,
                round(self.DEGtoDMM(val=self.lngDEG), 4), self.ew,
                self.kmH, self.heading, self.utc.strftime(self.ymdFormat), self.md, self.ew, self.statS]
        return self.toNMEA(src=item)

    def ZDA(self) -> bytes:
        item = ['GPZDA',
                self.utc.strftime(self.hmsFormatP)[:-3],
                self.utc.strftime('%d'), self.utc.strftime('%m'), self.utc.strftime('%Y'),
                self.offsetT, self.offsetM]
        return self.toNMEA(src=item)

    def headingToRadian(self, *, heading: float):
        return math.radians((heading * -1) + 90)

    def setHeading(self, *, val: float) -> None:
        self.heading = val

    def DEGtoDMM(self, *, val: float) -> float:
        '''
        GoogleMap等で使われるDegree形式からNMEAで使われるDMM形式への変換
        :param val:
        :return: float
        '''

        decimal, integer = math.modf(val)
        value = (integer + ((decimal * 60) / 100)) * 100
        return value

    def DMMtoDEG(self, *, val: float) -> float:
        '''
        DEGtoDMMの逆
        :param val:
        :return: float
        '''
        decimal, integer = math.modf(val)
        value = (integer // 100) + ((integer % 100) / 60) + (decimal / 60)

        return value

    def stop(self):
        self.running = False

    def run(self) -> None:
        while self.running:
            time.sleep(1)
            with self.locker:
                now = dt.utcnow()
                secs = (now - self.utc).total_seconds()  # 経過秒数の取得
                self.utc = now

                dist = (self.kmH * secs) / (60 * 60)  # 移動距離(m)
                # logger.debug(f'speed = {self.kmH:.1f}km/H distance = {dist*1000:.1f}m')
                radian = self.headingToRadian(heading=self.heading)  # 方位(真上が0で時計回りな座標系)

                latPlus = math.sin(radian) * dist * self.meterPerAngle
                lngPlus = math.cos(radian) * dist * self.meterPerAngle

                latSec = (self.latDEG * 3600) + latPlus
                lngSec = (self.lngDEG * 3600) + lngPlus

                self.latDEG = latSec / 3600
                self.lngDEG = lngSec / 3600

                # logger.debug(
                #     f'{self.kmH}kmH * {secs:.1f} = {dist * 1000:.1f}m -> lat/lng={self.latDEG:.6f}/{self.lngDEG:.6f}')

                self.location.GPGGA = self.GGA()
                self.location.GPGLL = self.GLL()
                self.location.GPRMC = self.RMC()
                self.location.GPZDA = self.ZDA()
                self.GPSready.set()


if __name__ == '__main__':
    def main():
        C = Cockpit(latDEG=35.602119, lngDEG=139.368418, kmH=36, heading=60)
        C.start()
        while True:
            if C.GPSready.wait(timeout=5):
                C.GPSready.clear()
                print(C.location)


    main()
