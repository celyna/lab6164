import socket 
import sys
from check import ip_checksum
from time import sleep

HOST = ''
PORT = 2155
PKT = 1

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

  if data[3:5] != ip_checksum(data[5:]): 
    continue
  
  RCVPKT = int(data[0:3])
  ACK = RCVPKT
  #if not the packet we are waiting for re-ack previous packet
  if RCVPKT != PKT: #not the right packet, send ACK of older packet
    ACK = PKT - 1   #resend the previous PKT
    print 'UNEXPECTED RCVPKT'
  #packet we are waiting for, send next pkt
  else: 
    PKT += 1
  reply = str(ACK).zfill(3) + data[3:]
  s.sendto(reply, addr)
  print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()

s.close()


