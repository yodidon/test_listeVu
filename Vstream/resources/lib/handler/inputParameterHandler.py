# -*- coding: utf-8 -*-
# vStream https://github.com/Kodi-vStream/venom-xbmc-addons
DEBUG = False
if DEBUG:

    import sys  # pydevd module need to be copied in Kodi\system\python\Lib\pysrc
    #sys.path.append('H:\Program Files\Kodi\system\Python\Lib\pysrc')

    try:
        import pydevd  # with the addon script.module.pydevd, only use `import pydevd`
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " + "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")

import sys

from resources.lib.util import UnquotePlus, Unquote


class cInputParameterHandler:
    def __init__(self):
        aParams = dict()
        if len(sys.argv) >= 2 and len(sys.argv[2]) > 0:
            args = sys.argv[2].replace(' & ', ' ')
            aParams = dict(part.split('=') for part in args[1:].split('&'))

        self.__aParams = aParams

    def getAllParameter(self):
        return self.__aParams

    def getValue(self, sParamName):
        if self.exist(sParamName):
            sParamValue = self.__aParams[sParamName]
            if not sParamValue.startswith('http'):
                return UnquotePlus(sParamValue)
            else:
                return Unquote(sParamValue)
        return False

    def exist(self, sParamName):
        if sParamName in self.__aParams:
            return sParamName
