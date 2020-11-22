from dataclasses import dataclass
import responder


class Constatnts(object):
    class DateTime(object):
        timeFormat = '%Y-%m-%d %H:%M:%S.%f'


@dataclass()
class GPSSensor(object):
    GPGGA: bytes = b''
    GPGLL: bytes = b''
    GPRMC: bytes = b''
    GPZDA: bytes = b''


@dataclass()
class GoogleMapLatLng(object):
    mode: str = 'GPS'
    lat: float = 0.0
    lng: float = 0.0
    spd: float = 0.0
    hdg: float = 0.0
    acc: float = 0.0
    at: str = ''
