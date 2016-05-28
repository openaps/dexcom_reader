import crc16
import constants
import struct
import util
import binascii


class BaseDatabaseRecord(object):
  FORMAT = None

  @classmethod
  def _CheckFormat(cls):
    if cls.FORMAT is None or not cls.FORMAT:
      raise NotImplementedError("Subclasses of %s need to define FORMAT"
                                % cls.__name__)

  @classmethod
  def _ClassFormat(cls):
    cls._CheckFormat()
    return struct.Struct(cls.FORMAT)

  @classmethod
  def _ClassSize(cls):
    return cls._ClassFormat().size

  @property
  def FMT(self):
    self._CheckFormat()
    return _ClassFormat()

  @property
  def SIZE(self):
    return self._ClassSize()

  @property
  def crc(self):
    return self.data[-1]

  def __init__(self, data, raw_data):
    self.raw_data = raw_data
    self.data = data
    self.check_crc()

  def check_crc(self):
    local_crc = self.calculate_crc()
    if local_crc != self.crc:
      raise constants.CrcError('Could not parse %s' % self.__class__.__name__)

  def dump(self):
    return ''.join('\\x%02x' % ord(c) for c in self.raw_data)

  def calculate_crc(self):
    return crc16.crc16(self.raw_data[:-2])

  @classmethod
  def Create(cls, data, record_counter):
    offset = record_counter * cls._ClassSize()
    raw_data = data[offset:offset + cls._ClassSize()]
    unpacked_data = cls._ClassFormat().unpack(raw_data)
    return cls(unpacked_data, raw_data)


class GenericTimestampedRecord(BaseDatabaseRecord):
  FIELDS = [ ]
  BASE_FIELDS = [ 'system_time', 'display_time' ]
  @property
  def system_time(self):
    return util.ReceiverTimeToTime(self.data[0])

  @property
  def display_time(self):
    return util.ReceiverTimeToTime(self.data[1])


  def to_dict (self):
    d = dict( )
    for k in self.BASE_FIELDS + self.FIELDS:
      d[k] = getattr(self, k)
      if callable(getattr(d[k], 'isoformat', None)):
        d[k] = d[k].isoformat( )
    return d

class GenericXMLRecord(GenericTimestampedRecord):
  FORMAT = '<II490sH'

  @property
  def xmldata(self):
    data = self.data[2].replace("\x00", "")
    return data


class InsertionRecord(GenericTimestampedRecord):
  FIELDS = ['insertion_time', 'session_state']
  FORMAT = '<3IcH'

  @property
  def insertion_time(self):
    if self.data[2] == 0xFFFFFFFF:
      return self.system_time
    return util.ReceiverTimeToTime(self.data[2])

  @property
  def session_state(self):
    states = [None, 'REMOVED', 'EXPIRED', 'RESIDUAL_DEVIATION',
              'COUNTS_DEVIATION', 'SECOND_SESSION', 'OFF_TIME_LOSS',
              'STARTED', 'BAD_TRANSMITTER', 'MANUFACTURING_MODE',
              'UNKNOWN1', 'UNKNOWN2', 'UNKNOWN3', 'UNKNOWN4', 'UNKNOWN5',
              'UNKNOWN6', 'UNKNOWN7', 'UNKNOWN8']
    return states[ord(self.data[3])]

  def __repr__(self):
    return '%s:  state=%s' % (self.display_time, self.session_state)

class G5InsertionRecord (InsertionRecord):
  FORMAT = '<3Ic10BH'

class Calibration(GenericTimestampedRecord):
  FORMAT = '<2Iddd3cdb'
  # CAL_FORMAT = '<2Iddd3cdb'
  FIELDS = [ 'slope', 'intercept', 'scale', 'decay', 'numsub', 'raw' ]
  @property
  def raw (self):
    return binascii.hexlify(self.raw_data)
  @property
  def slope  (self):
    return self.data[2]
  @property
  def intercept  (self):
    return self.data[3]
  @property
  def scale (self):
    return self.data[4]
  @property
  def decay (self):
    return self.data[8]
  @property
  def numsub (self):
    return int(self.data[9])

  def __repr__(self):
    return '%s: CAL SET:%s' % (self.display_time, self.raw)

  LEGACY_SIZE = 148
  REV_2_SIZE = 249
  @classmethod
  def _ClassSize(cls):

    return cls.REV_2_SIZE

  @classmethod
  def Create(cls, data, record_counter):
    offset = record_counter * cls._ClassSize()
    cal_size = struct.calcsize(cls.FORMAT)
    raw_data = data[offset:offset + cls._ClassSize()]

    cal_data = data[offset:offset + cal_size]
    unpacked_data = cls._ClassFormat().unpack(cal_data)
    return cls(unpacked_data, raw_data)

  def __init__ (self, data, raw_data):
    self.page_data = raw_data
    self.raw_data = raw_data
    self.data = data
    subsize = struct.calcsize(SubCal.FORMAT)
    offset = self.numsub * subsize
    calsize = struct.calcsize(self.FORMAT)
    caldata = raw_data[:calsize]
    subdata = raw_data[calsize:calsize + offset]
    crcdata = raw_data[calsize+offset:calsize+offset+2]

    subcals = [ ]
    for i in xrange(self.numsub):
      offset = i * subsize
      raw_sub = subdata[offset:offset+subsize]
      sub = SubCal(raw_sub, self.data[1])
      subcals.append(sub)

    self.subcals = subcals

    self.check_crc()
  def to_dict (self):
    res = super(Calibration, self).to_dict( )
    res['subrecords'] = [ sub.to_dict( ) for sub in  self.subcals ]
    return res
  @property
  def crc(self):
    return struct.unpack('H', self.raw_data[-2:])[0]

class LegacyCalibration (Calibration):
  @classmethod
  def _ClassSize(cls):

    return cls.LEGACY_SIZE


class SubCal (GenericTimestampedRecord):
  FORMAT = '<IIIIc'
  BASE_FIELDS = [ ]
  FIELDS = [ 'entered', 'meter',  'sensor', 'applied', ]
  def __init__ (self, raw_data, displayOffset=None):
    self.raw_data = raw_data
    self.data = self._ClassFormat().unpack(raw_data)
    self.displayOffset = displayOffset
  @property
  def entered  (self):
    return util.ReceiverTimeToTime(self.data[0])
  @property
  def meter  (self):
    return int(self.data[1])
  @property
  def sensor  (self):
    return int(self.data[2])
  @property
  def applied  (self):
    return util.ReceiverTimeToTime(self.data[3])

class MeterRecord(GenericTimestampedRecord):
  FORMAT = '<2IHIH'
  FIELDS = ['meter_glucose', 'meter_time' ]

  @property
  def meter_glucose(self):
    return self.data[2]

  @property
  def meter_time(self):
    return util.ReceiverTimeToTime(self.data[3])

  def __repr__(self):
    return '%s: Meter BG:%s' % (self.display_time, self.meter_glucose)

class G5MeterRecord (MeterRecord):
  FORMAT = '<2IHI5BH'

class EventRecord(GenericTimestampedRecord):
  # sys_time,display_time,glucose,meter_time,crc
  FORMAT = '<2I2c2IH'
  FIELDS = ['event_type', 'event_sub_type', 'event_value' ]

  @property
  def event_type(self):
    event_types = [None, 'CARBS', 'INSULIN', 'HEALTH', 'EXCERCISE',
                    'MAX_VALUE']
    return event_types[ord(self.data[2])]

  @property
  def event_sub_type(self):
    subtypes = {'HEALTH': [None, 'ILLNESS', 'STRESS', 'HIGH_SYMPTOMS',
                            'LOW_SYMTOMS', 'CYCLE', 'ALCOHOL'],
                'EXCERCISE': [None, 'LIGHT', 'MEDIUM', 'HEAVY',
                              'MAX_VALUE']}
    if self.event_type in subtypes:
      return subtypes[self.event_type][ord(self.data[3])]

  @property
  def display_time(self):
    return util.ReceiverTimeToTime(self.data[4])

  @property
  def event_value(self):
    value = self.data[5]
    if self.event_type == 'INSULIN':
      value = value / 100.0
    return value

  def __repr__(self):
    return '%s:  event_type=%s sub_type=%s value=%s' % (self.display_time, self.event_type,
                                    self.event_sub_type, self.event_value)

class SensorRecord(GenericTimestampedRecord):
  # uint, uint, uint, uint, ushort
  # (system_seconds, display_seconds, unfiltered, filtered, rssi, crc)
  FORMAT = '<2IIIhH'
  # (unfiltered, filtered, rssi)
  FIELDS = ['unfiltered', 'filtered', 'rssi']
  @property
  def unfiltered(self):
    return self.data[2]

  @property
  def filtered(self):
    return self.data[3]

  @property
  def rssi(self):
    return self.data[4]


class EGVRecord(GenericTimestampedRecord):
  # uint, uint, ushort, byte, ushort
  # (system_seconds, display_seconds, glucose, trend_arrow, crc)
  FIELDS = ['glucose', 'trend_arrow']
  FORMAT = '<2IHcH'

  @property
  def full_glucose(self):
    return self.data[2]

  @property
  def full_trend(self):
    return self.data[3]

  @property
  def display_only(self):
    return bool(self.full_glucose & constants.EGV_DISPLAY_ONLY_MASK)

  @property
  def glucose(self):
    return self.full_glucose & constants.EGV_VALUE_MASK

  @property
  def glucose_special_meaning(self):
    if self.glucose in constants.SPECIAL_GLUCOSE_VALUES:
      return constants.SPECIAL_GLUCOSE_VALUES[self.glucose]

  @property
  def is_special(self):
    return self.glucose_special_meaning is not None

  @property
  def trend_arrow(self):
    arrow_value = ord(self.full_trend) & constants.EGV_TREND_ARROW_MASK
    return constants.TREND_ARROW_VALUES[arrow_value]

  def __repr__(self):
    if self.is_special:
      return '%s: %s' % (self.display_time, self.glucose_special_meaning)
    else:
      return '%s: CGM BG:%s (%s) DO:%s' % (self.display_time, self.glucose,
                                           self.trend_arrow, self.display_only)

class G5EGVRecord (EGVRecord):
  FORMAT = '<2IHBBBBBBBBBcBH'
  @property
  def full_trend(self):
    return self.data[12]


