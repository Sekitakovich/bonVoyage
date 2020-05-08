from dataclasses import dataclass, asdict
from typing import Dict, List
import responder
import json


@dataclass()
class Place(object):
    name: str
    lat: float
    lng: float


class Main(responder.API):
    def __init__(self):
        super().__init__()

        self.add_route('/', self.top)

        self.place: List[Place] = [
            Place(name='函館支店', lat=41.766021, lng=140.718940),
            Place(name='釧路営業所', lat=42.982795, lng=144.383783),
            Place(name='稚内営業所', lat=45.409663, lng=141.674238),
            Place(name='仙台支店', lat=38.261555, lng=140.886887),
            Place(name='八戸営業所', lat=40.527124, lng=141.536147),
            Place(name='辰巳事業所', lat=35.652416, lng=139.809551),
            Place(name='焼津営業所', lat=34.863612, lng=138.321426),
            Place(name='関西支店', lat=34.698559, lng=135.490293),
            Place(name='高知営業所', lat=31.552530, lng=133.563696),
            Place(name='九州支店', lat=33.596823, lng=130.407840),
            Place(name='長崎営業所', lat=32.752861, lng=129.865224),
            Place(name='鹿児島営業所', lat=31.558395, lng=130.557021),
        ]

    def top(self, req: responder.Request, resp: responder.Response):
        resp.content = self.template(filename='main.html', place=self.place)


api = Main()

if __name__ == '__main__':
    api.run()
