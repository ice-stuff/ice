import json


class ExperimentTiming(object):
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self, ind_time):
        self.start_time = ind_time

    def end(self, ind_time):
        if self.start_time is None:
            raise ValueError('event has not started yet')
        self.end_time = ind_time

    def duration(self):
        if self.start_time is None:
            raise ValueError('event has not started yet')
        if self.end_time is None:
            raise ValueError('event has not ended yet')
        return self.end_time - self.start_time

    @classmethod
    def from_json(cls, json_str):
        object = cls()
        d = json.loads(json_str)
        object.start_time = d['start_time']
        object.end_time = d['end_time']
        return object

    def to_json(self):
        return json.dumps({
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
