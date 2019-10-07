if __package__ in {None, ''}:
    import constants
else:
    from . import constants
import datetime
import os
import platform
import plistlib
import re
import subprocess
import sys
import serial.tools.list_ports

def Ord(byte):
  if isinstance(byte, int):
    return byte
  elif isinstance(byte, str):
    return ord(byte)
  elif isinstance(byte, bytes):
    return int(byte[0])
  else:
    raise TypeError("unexpected class when changing to bytes: {class_name}".format(
        class_name=str(byte.__class__)
      )
    )

def python3():
  return sys.version_info[0] == 3

def to_bytes(iterable):
  return bytes(map(Ord, iterable))


def ReceiverTimeToTime(rtime):
  return constants.BASE_TIME + datetime.timedelta(seconds=rtime)


def linux_find_usbserial(vendor, product):
  DEV_REGEX = re.compile('^tty(USB|ACM)[0-9]+$')
  for usb_dev_root in os.listdir('/sys/bus/usb/devices'):
    device_name = os.path.join('/sys/bus/usb/devices', usb_dev_root)
    if not os.path.exists(os.path.join(device_name, 'idVendor')):
      continue
    idv = open(os.path.join(device_name, 'idVendor')).read().strip()
    if idv != vendor:
      continue
    idp = open(os.path.join(device_name, 'idProduct')).read().strip()
    if idp != product:
      continue
    for root, dirs, files in os.walk(device_name):
      for option in dirs + files:
        if DEV_REGEX.match(option):
          return os.path.join('/dev', option)


def osx_find_usbserial(vendor, product):
  def recur(v):
    if hasattr(v, '__iter__') and 'idVendor' in v and 'idProduct' in v:
      if v['idVendor'] == vendor and v['idProduct'] == product:
        tmp = v
        while True:
          if 'IODialinDevice' not in tmp and 'IORegistryEntryChildren' in tmp:
            tmp = tmp['IORegistryEntryChildren']
          elif 'IODialinDevice' in tmp:
            return tmp['IODialinDevice']
          else:
            break

    if type(v) == list:
      for x in v:
        out = recur(x)
        if out is not None:
          return out
    elif type(v) == dict or issubclass(type(v), dict):
      for x in list(v.values()):
        out = recur(x)
        if out is not None:
          return out

  sp = subprocess.Popen(['/usr/sbin/ioreg', '-k', 'IODialinDevice',
                         '-r', '-t', '-l', '-a', '-x'],
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, _ = sp.communicate()
  plist = plistlib.readPlistFromString(stdout)
  return recur(plist)

def windows_find_usbserial(vendor, product):
  ports = list(serial.tools.list_ports.comports())
  for p in ports:
    try:
      vid_pid_keyval = p.hwid.split()[1]
      vid_pid_val = vid_pid_keyval.split('=')[1]
      vid, pid = vid_pid_val.split(':')

      if vid.lower() != vendor.lower():
        continue
      if pid.lower() != product.lower():
        continue

      return p.device
    except (IndexError, ValueError) as e:
      continue

def find_usbserial(vendor, product):
  """Find the tty device for a given usbserial devices identifiers.

  Args:
     vendor: (int) something like 0x0000
     product: (int) something like 0x0000

  Returns:
     String, like /dev/ttyACM0 or /dev/tty.usb...
  """
  if platform.system() == 'Linux':
    vendor, product = [('%04x' % (x)).strip() for x in (vendor, product)]
    return linux_find_usbserial(vendor, product)
  elif platform.system() == 'Darwin':
    return osx_find_usbserial(vendor, product)
  elif platform.system() == 'Windows':
    vendor, product = [('%04x' % (x)).strip() for x in (vendor, product)]
    return windows_find_usbserial(vendor, product)
  else:
    raise NotImplementedError('Cannot find serial ports on %s'
                              % platform.system())

if __name__ == '__main__':
    vendor = constants.DEXCOM_USB_VENDOR
    product = constants.DEXCOM_USB_PRODUCT
    if len(sys.argv) > 1:
        vendor = int(sys.argv[1], 16)
    if len(sys.argv) > 2:
        product = int(sys.argv[2], 16)
    print(find_usbserial(vendor, product))
