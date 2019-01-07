import sys
import logging
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


class redisToSnmpTrapForwarder:

    def __init__(self,cliArgsDict):
        self.syslogMsgNumber = 0
        self.snmpTrapServer = cliArgsDict["snmpTrapServer"]
        self.snmpTrapPort = cliArgsDict["snmpTrapPort"]
        self.redisServer = cliArgsDict["redisServer"]
        self.trapCounter = 0
        self.mibBuilder = builder.MibBuilder()

        self.inputMibs = cliArgsDict["mibs"]
        self.srcDirectories = cliArgsDict["mibSources"]
        self.dstDirectory = cliArgsDict["mibCompileDir"]

        #self.inputMibs = ['RTBRICK-SYSLOG-MIB']
        #self.srcDirectories = ['/usr/share/snmp/mibs','/Users/Shared/snmp/mibs']
        #self.dstDirectory = '/Users/sli/.pysnmp/mibs'

        if cliArgsDict["compileMibs"]:
            mibCompiler = MibCompiler(SmiStarParser(),
                                      PySnmpCodeGen(),
                                      PyFileWriter(self.dstDirectory))
            logging.debug("mibCompiler {} {}".format(mibCompiler,self.dstDirectory))
            mibCompiler.addSources(*[FileReader(x) for x in self.srcDirectories])
            mibCompiler.addSearchers(PyFileSearcher(self.dstDirectory))
            mibCompiler.addSearchers(*[PyPackageSearcher(x) for x in PySnmpCodeGen.defaultMibPackages])
            mibCompiler.addSearchers(StubSearcher(*PySnmpCodeGen.baseMibs))
            results = mibCompiler.compile(*self.inputMibs)  #, rebuild=True, genTexts=True)
            logging.info('MibCompiler Results: %s' % ', '.join(['%s:%s' % (x, results[x]) for x in results]))

        compiler.addMibCompiler(self.mibBuilder, sources=self.srcDirectories)
        self.mibViewController = view.MibViewController(self.mibBuilder)
        for mib in self.inputMibs:
            self.mibBuilder.loadModules( mib )
            logging.debug("mibBuilder.loadModules( {} )".format(mib))

        self.snmpVersion = cliArgsDict["version"]
        if self.snmpVersion == "2c":
            self.community = cliArgsDict["community"]
            logging.info("SNMP version {} community {}".format(self.snmpVersion,self.community))
            #config.addV1System(self.snmpEngine, 'my-area', self.community )
        elif self.snmpVersion == "3":
            usmUserDataMatrix = [ usmUserTuple.strip().split(",") for usmUserTuple in cliArgsDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
            ### FIXME

        self.ntfOrg = ntforg.NotificationOriginator()

    def run_forever(self):
        logging.info('entering infinite while loop for processing rtbrickLogging-*-* keys from redis')
        while True:
            for key in self.redisServer.scan_iter("rtbrickLogging-*-*"):
                logging.debug ("processing redis key {}::{}".format(key,self.redisServer.get(key)))
                try:
                    bdsLogDict = json.loads(self.redisServer.get(key))
                except Exception as e:
                    logging.error ("connot load bdsLogDict:{} {}".format(self.redisServer.get(key),e))
                else:
                    logging.debug ("load bdsLogDict: {}".format(bdsLogDict))
                    self.syslogMsgNumber += 1
                    try:
                        syslogMsgFacility = bdsLogDict["host"]
                    except Exception as e:
                        logging.error ("connot set syslogMsgFacility from bdsLogDict: {}".format(bdsLogDict,e))
                        syslogMsgFacility = "error"
                    try:
                        syslogMsgSeverity = bdsLogDict["level"]
                    except Exception as e:
                        logging.error ("connot set syslogMsgSeverity from bdsLogDict: {}".format(bdsLogDict,e))
                        syslogMsgSeverity = 0
                    try:
                        syslogMsgText = bdsLogDict["full_message"]
                    except Exception as e:
                        logging.error ("connot set syslogMsgText from bdsLogDict: {}".format(bdsLogDict,e))
                        syslogMsgText = "error"
                    logging.debug ("data load {} {} {} {}".format(self.syslogMsgNumber,
                                syslogMsgFacility,
                                syslogMsgSeverity,
                                syslogMsgText))
                    errorIndication = self.ntfOrg.sendNotification(
                        ntforg.CommunityData(self.community),
                        ntforg.UdpTransportTarget((self.snmpTrapServer, self.snmpTrapPort)),
                        'trap',
                        ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'rtbrickSyslogTrap'),
                        #( ntforg.MibVariable('SNMPv2-MIB', 'sysUpTime', 0), 0 ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgNumber',   0), self.syslogMsgNumber ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgFacility', 0), syslogMsgFacility ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgSeverity', 0), syslogMsgSeverity ),
                        ( ntforg.MibVariable('RTBRICK-SYSLOG-MIB', 'syslogMsgText',     0), syslogMsgText )
                       )
                    if errorIndication:
                        logging.error ('Notification not sent: {}'.format(errorIndication))
                    else:
                        logging.debug ('Notification {} sent '.format(self.syslogMsgNumber))
                        self.redisServer.delete(key)
            time.sleep(0.001)

if __name__ == "__main__":
    epilogTXT = """

    ... to be added """

    parser = argparse.ArgumentParser(epilog=epilogTXT, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--logging", choices=['debug', 'warning', 'info'],
                        default='info', type=str,
                        help="Define logging level(debug=highest)")
    parser.add_argument('-s', '--snmpTrapServer', default='127.0.0.1',
                        help='specify SNMP server, which receives the traps', type=str)
    parser.add_argument('-p', '--snmpTrapPort', default=162,
                        help='snmp trap listening port, default is 162', type=int)
    parser.add_argument("-v","--version",  default='2c', type=str, choices=['2c', '3'],
                        help='specify snmp version')
    parser.add_argument("-c","--community",  default='public', type=str,
                        help='v2c community')
    parser.add_argument("-u","--usmUserTuples",  default='', type=str,
                        help='usmUserTuples engine,user,authkey,privkey list as comma separated string e.g:\n'+
                             '"80000a4c010a090150,usr-sha-aes128,authkey1,privkey1"')
    parser.add_argument('-m', '--mibs', default='RTBRICK-SYSLOG-MIB',
                        help='mib list as comma separated string', type=str)
    parser.add_argument('--mibSources', default="/usr/share/snmp/mibs,/Users/Shared/snmp/mibs",
                        help='mibSource list as comma separated string', type=str)
    parser.add_argument('--compileMibs',action='store_true')
    parser.add_argument('--mibCompileDir', default="/Users/sli/.pysnmp/mibs",
                        help='mibSource list as comma separated string', type=str)
    parser.add_argument('--redisServerIp', default='127.0.0.1',
                        help='redis server IP address, default is 127.0.0.1', type=str)
    parser.add_argument('--redisServerPort', default=6379,
                        help='redis Server port, default is 6379', type=int)
    parser.add_argument('-e', '--expiryTimer', default=3,
                        help='redis key expiry timer setting', type=int)
    cliargs = parser.parse_args()
    cliArgsDict = vars(cliargs)
    if cliArgsDict["logging"] == "debug":
        logging.getLogger().setLevel(logging.DEBUG)       # FIXME set level from cliargs
    elif cliArgsDict["logging"] == "warning":
        logging.getLogger().setLevel(logging.WARNING)       # FIXME set level from cliargs
    else:
        logging.getLogger().setLevel(logging.INFO)       # FIXME set level from cliargs
    logging.debug("cliArgsDict: {}".format(cliArgsDict))
    cliArgsDict["mibSources"] = [source.strip() for source in cliArgsDict["mibSources"].split(',') if len(source) > 0 ]
    logging.debug("cliArgsDict['mibSources']: {}".format(cliArgsDict["mibSources"]))
    cliArgsDict["mibs"] = [ mib.strip() for mib in cliArgsDict["mibs"].split(',') if len(mib) > 0 ]
    logging.debug("cliArgsDict['mibs']: {}".format(cliArgsDict["mibs"]))
    cliArgsDict["usmUserDataMatrix"] = [ usmUserTuple.strip().split(",") for usmUserTuple in cliArgsDict["usmUserTuples"].split(';') if len(usmUserTuple) > 0 ]
    logging.debug("cliArgsDict['usmUserDataMatrix']: {}".format(cliArgsDict["usmUserDataMatrix"]))
    cliArgsDict["usmUsers"] = []
    cliArgsDict["redisServer"] = redis.StrictRedis(host=cliArgsDict["redisServerIp"], port=cliArgsDict["redisServerPort"], db=0,decode_responses=True)
    logging.info("redis client started: {}".format(cliArgsDict["redisServer"]))
    myRedisToSnmpForwarder = redisToSnmpTrapForwarder(cliArgsDict)
    myRedisToSnmpForwarder.run_forever()
