from ariadne.asgi import GraphQL


class FrazzlGQL(GraphQL):

    def __init__(self, schema, startup, shutdown, **kwargs):
        super(FrazzlGQL, self).__init__(schema, **kwargs)
        self.startup = startup
        self.shutdown = shutdown

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message['type'] == 'lifespan.startup':
                    self.startup()
                    await send({'type': 'lifespan.startup.complete'})
                elif message['type'] == 'lifespan.shutdown':
                    self.shutdown()
                    await send({'type': 'lifespan.shutdown.complete'})
                    return

        await super(FrazzlGQL, self).__call__(scope, receive, send)
