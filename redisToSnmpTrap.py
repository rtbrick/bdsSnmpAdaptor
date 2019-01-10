import sys
import logging
from logging.handlers import RotatingFileHandler
import argparse
import redis
import time
import json
from pysnmp.entity.rfc3413.oneliner import ntforg
from pysnmp.smi import builder, view, compiler, rfc1902

from pysmi.reader import FileReader
from pysmi.searcher import PyFileSearcher, PyPackageSearcher, StubSearcher
from pysmi.writer import PyFileWriter
from pysmi.parser import SmiStarParser
from pysmi.codegen import PySnmpCodeGen
from pysmi.compiler import MibCompiler

from bdsSnmpAdapterManager import loadBdsSnmpAdapterConfigFile


class redisToSnmpTrapForwarder:


    def set_logging(self,configDict):
        logging.root.handlers = []
        self.moduleLogger = logging.getLogger('redisToSnmpTrap')
        logFile = configDict['rotatingLogFile'] + "redisToSnmpTrap.log"
        #
        #logging.basicConfig(filename=logFile, filemode='w', level=logging.DEBUG)
        rotateHandler = RotatingFileHandler(logFile, maxBytes=1000000,backupCount=2)  #1M rotating log
        formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
        rotateHandler.setFormatter(formatter)
        logging.getLogger("").addHandler(rotateHandler)
        #
        self.loggingLevel = configDict['loggingLevel']
        if self.loggingLevel in ["debug", "info", "warning"]:
            if self.loggingLevel == "debug": logging.getLogger().setLevel(logging.DEBUG)
            if self.loggingLevel == "info": logging.getLogger().setLevel(logging.INFO)
            if self.loggingLevel == "warning": logging.getLogger().setLevel(logging.WARNING)
        self.moduleLogger.info("self.loggingLevel: {}".format(self.loggingLevel))



    def __init__(self,cliArgsDict):
        self.moduleLogger = logging.getLogger('redisToSnmpTrap')
        configDict = loadBdsSnmpAdapterConfigFile(cliArgsDict["configFile"],"redisToSnmpTrap")
        self.set_logging(configDict)
        self.moduleLogger.debug("configDict:{}".format(configDict))
        self.redisServer = redis.StrictRedis(host=configDict["redisServerIp"], port=configDict["redisServerPort"], db=0,decode_responses=True)

        self.moduleLogger.info("original configDict: {}".format(configDict))
        configDict["mibSources"] = [source.strip() for source in configDict["mibSources"].split(',') if len(source) > 0 ]
        self.moduleLogger.debug("configDict['mibSources']: {}".format(configDict["mibSources"]))
        configDict["mibs"] = [ mib.strip() for mib in configDict["mibs"].split(',') if len(mib) > 0 ]
        self.moduleLogger.debug("configDict['mibs']: {}".format(configDict["mibs"]))
        configDict["usmUserDataMatrix"] = [ usmUserTuple.strip().split(",") for usmUserTuple in configDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
        self.moduleLogger.debug("configDict['usmUserDataMatrix']: {}".format(configDict["usmUserDataMatrix"]))
        configDict["usmUsers"] = []
        self.moduleLogger.info("modified configDict: {}".format(configDict))

        self.snmpTrapServer = configDict["snmpTrapServer"]
        self.snmpTrapPort = configDict["snmpTrapPort"]
        self.trapCounter = 0
        self.mibBuilder = builder.MibBuilder()

        self.inputMibs = configDict["mibs"]
        self.srcDirectories = configDict["mibSources"]
        self.dstDirectory = configDict["mibCompileDir"]
        self.trapCounter = 0

        #self.inputMibs = ['RTBRICK-SYSLOG-MIB']
        #self.srcDirectories = ['/usr/share/snmp/mibs','/Users/Shared/snmp/mibs']
        #self.dstDirectory = '/Users/sli/.pysnmp/mibs'

        if configDict["compileMibs"]:
            mibCompiler = MibCompiler(SmiStarParser(),
                                      PySnmpCodeGen(),
                                      PyFileWriter(self.dstDirectory))
            self.moduleLogger.debug("mibCompiler {} {}".format(mibCompiler,self.dstDirectory))
            mibCompiler.addSources(*[FileReader(x) for x in self.srcDirectories])
            mibCompiler.addSearchers(PyFileSearcher(self.dstDirectory))
            mibCompiler.addSearchers(*[PyPackageSearcher(x) for x in PySnmpCodeGen.defaultMibPackages])
            mibCompiler.addSearchers(StubSearcher(*PySnmpCodeGen.baseMibs))
            results = mibCompiler.compile(*self.inputMibs)  #, rebuild=True, genTexts=True)
            self.moduleLogger.info('MibCompiler Results: %s' % ', '.join(['%s:%s' % (x, results[x]) for x in results]))

        compiler.addMibCompiler(self.mibBuilder, sources=self.srcDirectories)
        self.mibViewController = view.MibViewController(self.mibBuilder)
        for mib in self.inputMibs:
            self.mibBuilder.loadModules( mib )
            self.moduleLogger.debug("mibBuilder.loadModules( {} )".format(mib))

        self.snmpVersion = configDict["version"]
        if self.snmpVersion == "2c":
            self.community = configDict["community"]
            self.moduleLogger.info("SNMP version {} community {}".format(self.snmpVersion,self.community))
            #config.addV1System(self.snmpEngine, 'my-area', self.community )
        elif self.snmpVersion == "3":
            usmUserDataMatrix = [ usmUserTuple.strip().split(",") for usmUserTuple in configDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
            ### FIXME

        self.ntfOrg = ntforg.NotificationOriginator()

    def run_forever(self):
        self.moduleLogger.info('entering infinite while loop for processing rtbrickLogging-*-* keys from redis')
        while True:
            for key in self.redisServer.scan_iter("rtbrickLogging-*-*"):
                self.moduleLogger.debug ("processing redis key {}::{}".format(key,self.redisServer.get(key)))
                try:
                    bdsLogDict = json.loads(self.redisServer.get(key))
                except Exception as e:
                    self.moduleLogger.error ("connot load bdsLogDict:{} {}".format(self.redisServer.get(key),e))
                else:
                    self.moduleLogger.debug ("load bdsLogDict: {}".format(bdsLogDict))
                    self.trapCounter += 1
                    try:
                        syslogMsgFacility = bdsLogDict["host"]
                    except Exception as e:
                        self.moduleLogger.error ("connot set syslogMsgFacility from bdsLogDict: {}".format(bdsLogDict,e))
                        syslogMsgFacility = "error"
                    try:
                        syslogMsgSeverity = bdsLogDict["level"]
                    except Exception as e:
                        self.moduleLogger.error ("connot set syslogMsgSeverity from bdsLogDict: {}".format(bdsLogDict,e))
                        syslogMsgSeverity = 0
                    try:
                        syslogMsgText = bdsLogDict["full_message"]
                    except Exception as e:
                        self.moduleLogger.error ("connot set syslogMsgText from bdsLogDict: {}".format(bdsLogDict,e))
                        syslogMsgText = "error"
                    self.moduleLogger.debug ("data load {} {} {} {}".format(self.trapCounter,
                                syslogMsgFacility,
                                syslogMsgSeverity,
                                syslogMsgText))
                    errorIndication = self.ntfOrg.sendNotification(
                        ntforg.CommunityData(self.community),
                        ntforg.UdpTransportTarget((self.snmpTrapServer, self.snmpTrapPort)),
                        'trap',
                        ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'rtbrickSyslogTrap'),
                        #( ntforg.MibVariable('SNMPv2-MIB', 'sysUpTime', 0), 0 ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgNumber',   0), self.trapCounter ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgFacility', 0), syslogMsgFacility ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgSeverity', 0), syslogMsgSeverity ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgText',     0), syslogMsgText )
                       )
                    if errorIndication:
                        self.moduleLogger.error ('Notification not sent: {}'.format(errorIndication))
                    else:
                        self.moduleLogger.debug ('Notification {} sent '.format(self.trapCounter))
                        self.redisServer.delete(key)
            time.sleep(0.001)

if __name__ == "__main__":
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--configFile",
                            default="/etc/bdsSnmpAdapterConfig.yml", type=str,
                            help="config file")

    # parser.add_argument("--logging", choices=['debug', 'warning', 'info'],
    #                     default='info', type=str,
    #                     help="Define logging level(debug=highest)")
    # parser.add_argument('-s', '--snmpTrapServer', default='127.0.0.1',
    #                     help='specify SNMP server, which receives the traps', type=str)
    # parser.add_argument('-p', '--snmpTrapPort', default=162,
    #                     help='snmp trap destination port, default is 162', type=int)
    # parser.add_argument("-v","--version",  default='2c', type=str, choices=['2c', '3'],
    #                     help='specify snmp version')
    # parser.add_argument("-c","--community",  default='public', type=str,
    #                     help='v2c community')
    # parser.add_argument("-u","--usmUserTuples",  default='', type=str,
    #                     help='usmUserTuples engine,user,authkey,privkey list as comma separated string e.g:\n'+
    #                          '"80000a4c010a090150,usr-sha-aes128,authkey1,privkey1"')
    # parser.add_argument('-m', '--mibs', default='RTBRICK-SYSLOG-MIB',
    #                     help='mib list as comma separated string', type=str)
    # parser.add_argument('--mibSources', default="/usr/share/snmp/mibs,/Users/Shared/snmp/mibs",
    #                     help='mibSource list as comma separated string', type=str)
    # parser.add_argument('--compileMibs',action='store_true')
    # parser.add_argument('--mibCompileDir', default="/Users/sli/.pysnmp/mibs",
    #                     help='mibSource list as comma separated string', type=str)
    # parser.add_argument('--redisServerIp', default='127.0.0.1',
    #                     help='redis server IP address, default is 127.0.0.1', type=str)
    # parser.add_argument('--redisServerPort', default=6379,
    #                     help='redis Server port, default is 6379', type=int)
    # parser.add_argument('-e', '--expiryTimer', default=3,
    #                     help='redis key expiry timer setting', type=int)
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    # if cliArgsDict["logging"] == "debug":
    #     logging.getLogger().setLevel(logging.DEBUG)       # FIXME set level from cliargs
    # elif cliArgsDict["logging"] == "warning":
    #     logging.getLogger().setLevel(logging.WARNING)       # FIXME set level from cliargs
    # else:
    #     logging.getLogger().setLevel(logging.INFO)       # FIXME set level from cliargs
    # logging.debug("cliArgsDict: {}".format(cliArgsDict))
    # cliArgsDict["mibSources"] = [source.strip() for source in cliArgsDict["mibSources"].split(',') if len(source) > 0 ]
    # logging.debug("cliArgsDict['mibSources']: {}".format(cliArgsDict["mibSources"]))
    # cliArgsDict["mibs"] = [ mib.strip() for mib in cliArgsDict["mibs"].split(',') if len(mib) > 0 ]
    # logging.debug("cliArgsDict['mibs']: {}".format(cliArgsDict["mibs"]))
    # cliArgsDict["usmUserDataMatrix"] = [ usmUserTuple.strip().split(",") for usmUserTuple in cliArgsDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
    # logging.debug("cliArgsDict['usmUserDataMatrix']: {}".format(cliArgsDict["usmUserDataMatrix"]))
    # cliArgsDict["usmUsers"] = []
    # cliArgsDict["redisServer"] = redis.StrictRedis(host=cliArgsDict["redisServerIp"], port=cliArgsDict["redisServerPort"], db=0,decode_responses=True)
    # logging.info("redis client started: {}".format(cliArgsDict["redisServer"]))
    myRedisToSnmpForwarder = redisToSnmpTrapForwarder(cliArgsDict)
    myRedisToSnmpForwarder.run_forever()
