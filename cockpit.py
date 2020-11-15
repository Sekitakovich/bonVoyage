from dataclasses import dataclass
from datetime import datetime as dt
import math
import time

from common import GPS, Constatnts


class Cockpit(object):
    def __init__(self, *, latDEG: float = 0, lngDEG: float = 0, kmH: float = 0, heading: float = 0):
        self.latDMM = self.DEGtoDMM(val=latDEG)
        self.lngDMM = self.DEGtoDMM(val=lngDEG)
        self.kmH = kmH
        self.heading = heading
        self.lastDT = dt.now()

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

    def current(self) -> GPS:
        utc = dt.utcnow()
        now = dt.now()
        secs = (now - self.lastDT).total_seconds()  # 経過秒数の取得
        self.lastDT = now

        dist = (self.kmH * secs) / (60 * 60)  # 移動距離(m)
        radian = self.headingToRadian(heading=self.heading)  # 方位(真上が0で時計回りな座標系)
        self.latDMM += math.sin(radian) * dist
        self.lngDMM += math.cos(radian) * dist

        return GPS(latDMM=self.latDMM, lngDMM=self.lngDMM, spdKMH=self.kmH, heading=self.heading, at=utc.strftime(Constatnts.DateTime.timeFormat))


if __name__ == '__main__':
    def main():
        C = Cockpit(kmH=100)
        for a in range(10):
            time.sleep(1)
            ooo = C.current()
            print(ooo)


    main()
