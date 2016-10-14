'''Key-value store abstraction'''
import os

from chineurs import settings


class Storage:
    '''Key-value store abstraction'''

    def __init__(self, uuid):
        '''Sets up storage'''
        self.uuid = uuid
        self.directory = os.path.join(settings.DATA_DIRECTORY, uuid)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def get(self, key):
        '''Gets the given key from storage if it exists'''
        filename = os.path.join(self.directory, key)
        if not os.path.isfile(filename):
            return None
        with open(filename) as handle:
            return handle.read().strip()

    def set(self, key, value):
        '''Stores the given key value pair'''
        with open(os.path.join(self.directory, key), 'w') as handle:
            handle.write(value)
