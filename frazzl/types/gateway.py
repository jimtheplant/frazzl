class Gateway:

    def __init__(self):
        self.services = []
        self.schema = None

    def add_service(self, service):
        service_schema = service.schema
