import random

from utils.fish_logging import load_logger

logger = load_logger()


class STM_fake:
    def __init__(self, tty, tm):
        self.tty = tty
        self.init(tm)

    def init(self, tm):
        self.s = None

    def hello(self, tty):
        rpl = b'' if random.random() < 0.01 else b'167321907'
        if rpl == b'':
            logger.error('{} did not respond!!!'.format(tty))
            return 0
        try:
            rpl = int(rpl.strip().decode())
        except:
            logger.error('converting to int FAILED. {} responded: {}'.format(tty, rpl))
            return 0

        if rpl == 167321907:
            return 1
        else:
            return 0

    def GetTemperature(self, unit):
        try: 
            rpl = (25 + random.gauss(0, 0.2)) * 1000
            return (rpl / 1000.0)
        except:
            logger.error('temperature data read failed: unit #{}'.format(unit))
            return 7777777

    def GetIllumination(self, unit):
        try:
            unit += 128
            rpl = int(1020 + random.gauss(0, 10))
            return rpl
        except:
            logger.error('illumination data read failed: unit #{}'.format(unit))
            return 7777777

    def SwithcPowerOn(self, pwrtime):
        if random.random() < 0.01:
            logger.error('power switch failed')
            return 7777777
