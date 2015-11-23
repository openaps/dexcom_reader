import readdata

dd = readdata.Dexcom.FindDevice()
dr = readdata.Dexcom(dd)
meter_records = dr.ReadRecords('METER_DATA')
print 'First Meter Record = '
print meter_records[0]
print 'Last Meter Record ='  
print meter_records[-1]
insertion_records = dr.ReadRecords('INSERTION_TIME')
print 'First Insertion Record = '
print insertion_records[0]
print 'Last Insertion Record = '
print insertion_records[-1]
