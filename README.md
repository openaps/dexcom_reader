dexcom_reader
=============

This is a handful of scripts for dumping data from a Dexcom G4 Glucose Monitor
connected to a computer with USB.

Out of the box dumps data like:

    % python readdata.py
    Found Dexcom G4 Receiver S/N: SMXXXXXXXX
    Transmitter paired: 6XXXXX
    Battery Status: CHARGING (83%)
      Record count:
      - Meter records: 340
      - CGM records: 3340
      - CGM commitable records: 3340
      - Event records: 15
      - Insertion records: 4

Or like:

    % python dexcom_reader/dexcom_dumper.py  --g5 -n2
    2016-12-26 15:47:47: CGM BG:133 (FLAT) DO:False
    2016-12-26 15:52:45: CGM BG:127 (FLAT) DO:False
    2016-12-26 15:57:44: CGM BG:120 (FLAT) DO:False
    2016-12-26 16:02:44: CGM BG:116 (45_DOWN) DO:False
    2016-12-26 16:07:44: CGM BG:112 (45_DOWN) DO:False
    2016-12-26 16:12:44: CGM BG:113 (FLAT) DO:False
    2016-12-26 16:17:45: CGM BG:109 (FLAT) DO:False
    2016-12-26 16:22:51: CGM BG:102 (FLAT) DO:False
    2016-12-26 16:27:44: CGM BG:92 (45_DOWN) DO:False
    2016-12-26 16:32:44: CGM BG:86 (45_DOWN) DO:False
    2016-12-26 16:37:44: CGM BG:75 (45_DOWN) DO:False
    2016-12-26 16:42:44: CGM BG:63 (SINGLE_DOWN) DO:False
    2016-12-26 16:47:44: CGM BG:55 (SINGLE_DOWN) DO:False
    2016-12-26 16:52:44: CGM BG:52 (45_DOWN) DO:False
    2016-12-26 16:57:44: CGM BG:53 (FLAT) DO:False
    2016-12-26 17:02:44: CGM BG:60 (FLAT) DO:False
    2016-12-26 17:07:44: CGM BG:85 (SINGLE_UP) DO:False
    2016-12-26 17:12:44: CGM BG:107 (DOUBLE_UP) DO:False
    2016-12-26 17:17:44: CGM BG:121 (DOUBLE_UP) DO:False
    2016-12-26 17:22:44: CGM BG:131 (DOUBLE_UP) DO:False
    2016-12-26 17:27:45: CGM BG:144 (SINGLE_UP) DO:False
    2016-12-26 17:32:44: CGM BG:149 (45_UP) DO:False
    2016-12-26 17:37:44: CGM BG:153 (45_UP) DO:False
    2016-12-26 17:42:52: CGM BG:165 (45_UP) DO:False
    2016-12-26 17:47:55: CGM BG:176 (45_UP) DO:False

See also:

    % python dexcom_reader/dexcom_dumper.py  --help
    Usage: dexcom_dumper.py [options]

    Options:
      -h, --help      show this help message and exit
      --g4            use Dexcom G4 instead of Dexcom G5
      --g5            use Dexcom G5 instead of Dexcom G4
      -a, --all       dump all available records
      -n NUM_RECORDS  number of pages of CGM records to display
