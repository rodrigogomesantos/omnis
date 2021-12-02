import logging.config
import json
logging.config.dictConfig(json.loads(open(b'C:\Users\osche\OneDrive\Documentos\GitHub\Rose_ADP\engine\data\log\config\config.json', 'r').read()))
logger = logging.getLogger(__name__)

class customException(Exception):
    def __init__(self, *args):
        self.info = args[1]
        self.outputmessage = args[0]
        logger.error(f"{self.outputmessage} | {self.info}")
    def __str__(self):
        return self.outputmessage

class serialnotrespond(customException):
    def __init__(self, *args, **kwargs):
        customException.__init__(self, f"{args[0]} stop responding.", kwargs)    

class serialnotopen(customException):
    def __init__(self, *args, **kwargs):
        customException.__init__(self, f"{args[0]} failed to establish communication.", kwargs)

class axisundefined(customException):
    def __init__(self, *args, **kwargs):
        customException.__init__(self, f"axis {args[0]} is 'variable' in {args[1]}, but has undefined value in {args[2]}.", kwargs)

class M114unpackFail(customException):
    def __init__(self, *args, **kwargs):
            customException.__init__(self,f"{args[0]} can't unpack axis name from M114. Values are [{args[1]}]", args[1])