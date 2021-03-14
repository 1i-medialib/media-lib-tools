from pprint import pprint

class Logging:
    "MediaLib Utility/Logging class"

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
