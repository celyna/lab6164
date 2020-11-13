import socket 
import sys
from check import ip_checksum
from time import sleep

HOST = ''
PORT = 2155
PKT = 0

#COUNT = 0

try :
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  print "Socket created" 
except socket.error, msg :
  print 'Failed to create socket. Error Code: ' + str(msg[0]) + ' Message ' + msg[1] 
  sys.exit() 

try : 
  s.bind(("", PORT))
except socket.error, msg :
  print 'Bind failed. Error Code: ' + str(msg[0]) + ' Message ' + msg[1] 
  sys.exit() 

print 'Socket bind complete' 

while 1: 
  d = s.recvfrom(1024)
  data = d[0] 
  addr = d[1] 
  
  if not data: 
    break 

  if data[1:3] != ip_checksum(data[3:]): 
    continue
  
  ACK = data[0] 
  reply = str(ACK) + data[3:]
  s.sendto(reply, addr)
  if ACK != str(PKT): 
    print 'DUPLICATE'
  else: 
    PKT = 0 if PKT else 1
  print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()

  #COUNT += 1
  #if COUNT % 3 == 0:
  #  sleep(5)

s.close()