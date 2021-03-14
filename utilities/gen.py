from pprint import pprint
from utilities.logging import Logging

class Gen:
    "MediaLib Utility class"

    def __init__(self,verbose=False):
        self.verbose = verbose
        self.log = Logging()

    def duration_to_seconds(self,duration):
        seconds = 0
        self.log.debug('converting duration {} to seconds'.format(duration))
        # duration is XX:YY where XX is minutes and YY is Seconds
        pieces = duration.split(':')
        if len(pieces) == 1:
            self.log.debug('pieces[0] = {}'.format(pieces[0]))
            seconds = int(pieces[0])
        elif len(pieces) == 2:
            self.log.debug('pieces[0] = {}, pieces[1] = {}'.format(pieces[0], pieces[1]))
            seconds = int(pieces[1]) + (int(pieces[0]) * 60)
        else:
            self.log.log('Duration on supports 2 pieces')
            raise ValueError
        self.log.debug(
            'converted duration {} to seconds: {}'.format(duration, seconds))
        return seconds
