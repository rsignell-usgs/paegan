import json
from paegan.transport.models.behavior.diel import Diel
from paegan.transport.models.behavior.taxis import Taxis
from paegan.transport.models.behavior.capability import Capability

class LifeStage(object):

    def __init__(self, **kwargs):

        if 'json' in kwargs or 'data' in kwargs:
            data = {}
            try:
                data = json.loads(kwargs['json'])
            except:
                try:
                    data = kwargs.get('data')
                except:
                    pass

            self.name = data.get('name',None)
            self.linear_a = data.get('linear_a', None)
            self.linear_b = data.get('linear_b', None)
            self.duration = data.get('duration', None)
            self.diel = [Diel(data=d) for d in data.get('diel')]
            self.taxis = [Taxis(data=t) for t in data.get('taxis')]
            self.capability = Capability(data=data.get('capability'))

    def get_models(self):
        print len(self.diel)
