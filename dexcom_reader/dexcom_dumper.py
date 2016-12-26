import constants
import readdata

from optparse import OptionParser

G5_IS_DEFAULT = True
DEFAULT_PAGE_COUNT = 2

parser = OptionParser()
parser.add_option("--g4", action="store_false", dest="g5", default=G5_IS_DEFAULT, help="use Dexcom G4 instead of Dexcom G5")
parser.add_option("--g5", action="store_true",  dest="g5", default=G5_IS_DEFAULT, help="use Dexcom G5 instead of Dexcom G4")
parser.add_option("-a", "--all", action="store_true", dest="dump_everything", default=False, help="dump all available records")
parser.add_option("-n", type="int", dest="num_records", default=DEFAULT_PAGE_COUNT, help="number of pages of CGM records to display")

(options, args) = parser.parse_args()

def get_dexcom_reader():
        if options.g5:
                dd = readdata.DexcomG5.FindDevice()
                return readdata.DexcomG5(dd)
        else:
                dd = readdata.Dexcom.FindDevice()
                return readdata.Dexcom(dd)

dr = get_dexcom_reader()

if options.dump_everything:

#       record_types = ['METER_DATA', 'INSERTION_TIME', 'USER_EVENT_DATA', 'CAL_SET', 'SENSOR_DATA']

        unparseable = ['FIRMWARE_PARAMETER_DATA', 'RECEIVER_LOG_DATA', 'USER_SETTING_DATA', 'MAX_VALUE']
        parsed_to_xml = ['MANUFACTURING_DATA', 'PC_SOFTWARE_PARAMETER']
        skip = unparseable + parsed_to_xml + ['EGV_DATA']
        record_types = filter(lambda v: not v in skip, constants.RECORD_TYPES)

        for t in record_types:
                print t + ":"
                for r in dr.ReadRecords(t):
                        print r

cgm_records = dr.ReadRecords('EGV_DATA', 0 if options.dump_everything else options.num_records)
for cr in cgm_records:
        if not cr.display_only:
                print cr
