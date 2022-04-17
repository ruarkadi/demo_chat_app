import json
import copy

class MondoDecoder(json.JSONDecoder):
    def __init__(self):
        super().__init__(object_hook=self.normalize_id)

    def normalize_id(self, data):

        if '$oid' in data:
            data = data['$oid']

        if '_id' in data:
            data['id'] = data.pop('_id')

        return data

def normalize_data(data):
    return json.loads(data.to_json(), cls=MondoDecoder)
