class Block:
    def __init__(self, id, vehicle_task_id, start_time, dates, journeys):
        self.id = id
        self.vehicle_task_id = vehicle_task_id
        self.start_time = start_time
        self.dates = dates
        self.journeys = journeys


class Journey:
    def __init__(self, id, stops):
        self.id = id
        self.stops = stops


class Stop:
    def __init__(self, quay, departure_time):
        self.quay = quay
        self.departure_time = departure_time
