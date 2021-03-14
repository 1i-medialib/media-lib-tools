from pprint import pprint

class Utilities:
    "MediaLib Utility class"

    def __init__(self,verbose=False):
        self.verbose = verbose

    def log(self,msg):
        print(msg)
    
    def debug(self,msg):
        if self.verbose:
            self.log(msg)

    def pprintd(self,msg):
        if self.verbose:
            pprint(msg)

    def duration_to_seconds(self,duration):
        seconds = 0
        self.debug('converting duration {} to seconds'.format(duration))
        # duration is XX:YY where XX is minutes and YY is Seconds
        pieces = duration.split(':')
        if len(pieces) == 1:
            self.debug('pieces[0] = {}'.format(pieces[0]))
            seconds = int(pieces[0])
        elif len(pieces) == 2:
            self.debug('pieces[0] = {}, pieces[1] = {}'.format(pieces[0],pieces[1]))
            seconds = int(pieces[1]) + (int(pieces[0]) * 60)
        else:
            self.log('Duration on supports 2 pieces')
            raise ValueError
        self.debug('converted duration {} to seconds: {}'.format(duration,seconds))
        return seconds
