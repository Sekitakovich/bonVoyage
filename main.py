from dataclasses import dataclass, asdict
from typing import Dict, List
import responder
import json


# @dataclass()
# class LatLng(object):
#     lat: float
#     lng: float


class Main(responder.API):
    def __init__(self):
        super().__init__()

        self.add_route('/', self.top)

        self.place: Dict[str, Dict[str, float]] = {
            '函館支店': {'lat': 41.766021, 'lng': 140.718940},
            '釧路営業所': {'lat': 42.982795, 'lng': 144.383783},
            '稚内営業所': {'lat': 45.409663, 'lng': 141.674238},
            '仙台支店': {'lat': 38.261555, 'lng': 140.886887},
            '八戸営業所': {'lat': 40.527124, 'lng': 141.536147},
            '辰巳事業所': {'lat': 35.652416, 'lng': 139.809551},
            '焼津営業所': {'lat': 34.863612, 'lng': 138.321426},
            '関西支店': {'lat': 34.698559, 'lng': 135.490293},
            '高知営業所': {'lat': 33.552628, 'lng': 133.563733},
            '九州支店': {'lat': 33.596823, 'lng': 130.407840},
            '長崎営業所': {'lat': 32.752861, 'lng': 129.865224},
            '鹿児島営業所': {'lat': 31.558395, 'lng': 130.557021},
        }

        # id: int = 1
        # for k,v in self.place.items():
        #     print("insert into node(id,name,lat,lng) values(%d,'%s',%f,%f);" % (id,k,v['lat'],v['lng']))
        #     id += 1

    def top(self, req: responder.Request, resp: responder.Response):
        p: str = json.dumps(self.place, ensure_ascii=False)
        resp.content = self.template('main.html', place=p)


api = Main()

if __name__ == '__main__':
    api.run(address='0.0.0.0', port=80)
