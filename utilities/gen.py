from pprint import pprint
import logging
import re

logger = logging.getLogger(__name__)

class Gen:
    "MediaLib Utility class"

    def __init__(self,verbose=False):
        self.verbose = verbose

    def duration_to_seconds(self,duration):
        seconds = 0
        if type(duration).__name__ == 'float':
            seconds = int(duration)
        elif type(duration).__name__ == 'int':
            seconds = duration
        elif type(duration).__name__ == 'str':
            logger.debug('converting duration {} to seconds'.format(duration))
            # duration is XX:YY where XX is minutes and YY is Seconds
            pieces = duration.split(':')
            if len(pieces) == 1:
                logger.debug('pieces[0] = {}'.format(pieces[0]))
                seconds = int(pieces[0])
            elif len(pieces) == 2:
                logger.debug('pieces[0] = {}, pieces[1] = {}'.format(pieces[0], pieces[1]))
                seconds = int(pieces[1]) + (int(pieces[0]) * 60)
            else:
                logger.error('Duration on supports 2 pieces')
                raise ValueError
        else:
            logger.error('Can\'t convert duration type {}'.format(type(duration).__name__))
            raise ValueError
        logger.debug(
            'converted duration {} to seconds: {}'.format(duration, seconds))
        return seconds

    def convert_date(self,original_date):
        logger.debug('Need to convert date: {}, type: {}'.format(
            original_date, type(original_date).__name__))
        if type(original_date).__name__ == 'list':
            original_date = ''.join(str(original_date))

        fmt = '\\d\\d\\d\\d-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\dZ'
        match = re.match(fmt, original_date)
        if match:
            logger.debug('got a validate date/time, returning date')
            return

        fmt='\\d\\d\\d\\d\\Z'
        match = re.match(fmt,original_date)
        if match:
            logger.debug('got a validate year, returning date')
            return original_date + '-01-01'

        fmt = '\\d\\d\\d\\d\\-\\d\\d\\Z'
        match = re.match(fmt, original_date)
        if match:
            logger.debug('got a validate year, returning date')
            return original_date + '-01'

        return original_date