import socket 
import sys 
import select
from check import ip_checksum

HOST = 'localhost'
PORT = 2155
PKT = 0

COUNT = 0

try: 
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:    
  print 'Failed to create socket' 
  sys.exit() 

while 1: 
  msg = raw_input('Enter message to send : ')
  checksum = ip_checksum(msg)
  tmp = msg
  msg = str(PKT) + str(checksum) + msg

  while 1: 
    try:
      s.sendto(msg, (HOST, PORT))

      inputs = [s]
      outputs = [] 
      timeout = 3 
      readable, writeable, exceptional = select.select(inputs, outputs, inputs, timeout)
      d = ''
      for tempSocket in readable: 
        d = tempSocket.recvfrom(1024)
        reply = d[0] 
        addr = d[1] 
        print 'Server reply : ' + reply 
      if d == '' or str(PKT) != reply[0]:
        msg = str(PKT) + str(checksum) + tmp
        continue

    except socket.error, msg: 
      print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
      sys.exit() 
    
    break 

  PKT = 0 if PKT else 1