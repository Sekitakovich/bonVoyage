from dataclasses import dataclass
import responder


class Constatnts(object):
    class DateTime(object):
        timeFormat = '%Y-%m-%d %H:%M:%S.%f'


@dataclass()
class GPS(object):
    latDMM: float = 0.0
    lngDMM: float = 0.0
    spdKMH: float = 0.0
    heading: float = 0.0
    # acc: float = 0.0
    at: str = ''
