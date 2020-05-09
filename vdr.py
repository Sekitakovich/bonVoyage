'''
datagram of Voyage Data Recorders
'''

from typing import Dict, List
import json


class JCY1900(object):

    def __init__(self, *, sfi: bytes):
        self.counter: int = 0
        self.sfi = sfi

    def create(self, *, nmea: str) -> bytes:
        header: Dict[bytes, bytes] = {
            b's': self.sfi,
            b'n': self.counter,
        }

        header =

        self.counter += 1
        self.counter = self.counter % 10000


if __name__ == '__main__':
    pass
