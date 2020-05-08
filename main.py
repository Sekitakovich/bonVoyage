import responder


class Main(responder.API):
    def __init__(self):
        super().__init__()

        self.add_route('/', self.top)

    def top(self, req: responder.Request, resp: responder.Response):
        resp.content = self.template(filename='main.html')


api = Main()

if __name__ == '__main__':

    api.run()