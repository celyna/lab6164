import socket 
import sys 
import select
from check import ip_checksum
import time

def enum(**enums): 
  return type('Enum', (), enums) 
pkt_status = enum(NULL=0, READY=1, SENT=2, ACKED=3)

class pkt_struct: 
  def __init__(self, num, msg): 
    self.status = pkt_status.NULL
    self.num = num 
    self.msg = msg 
    self.time_sent = None
  def send_pkt(self, s): 
    s.sendto(self.msg, (HOST, PORT))
    self.time_sent = time.time()

#initializing 
pkt_list = list() #used as list of packets that havent been sent

HOST = 'localhost'
PORT = 2155
BASE = 1      #base for window
PKT = 1       #packet number
N = 4        #window size
TIMEOUT = 10  #timeout time

try: 
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:    
  print 'Failed to create socket' 
  sys.exit() 

while 1: 
  msg = raw_input('Enter message to send : ')
  checksum = ip_checksum(msg)     #get checksum of message
  msg = str(PKT).zfill(3) + str(checksum) + msg   #new message: 00PKT+CHKSM+MSG
  pkt_curr = pkt_struct(PKT, msg)   #current: packet with packet number and msg
  pkt_list.append(pkt_curr)         #add current packet to list of packets
  PKT += 1    #increment packet number

  #try to send packet
  try:
    if (pkt_curr.num < BASE + N):     #not sending packets outside of window
      pkt_curr.send_pkt(s) 
      #s.sendto(pkt_curr.msg, (HOST, PORT))  # send message to host:port
      #pkt_curr.time_sent = time.time()    #set time sent

    inputs = [s]
    outputs = [] 
    timeout = 1
    readable, writeable, exceptional = select.select(inputs, outputs, inputs, timeout)
    d = ''
    for tempSocket in readable: 
      d = tempSocket.recvfrom(1024)

      reply = d[0] 
      addr = d[1] 
      print 'Server reply : ' + reply 
    if d == '':
      continue    #Keep going until server replies with reply
    if (reply[3:5] == ip_checksum(reply[5:])) and (BASE == int(reply[0:3])): #dont move window if not sent successfully
      BASE += 1 #move window
      pkt_list.pop(0) #take off packetlist bc successful
      #send next packet 
      if len(pkt_list) >= N: #first N is transfering atm so anything greater than that needs to be sent
        pkt_list[N-1].sent_pkt(s)
        #s.sendto(pkt_list[N-1].msg, (HOST, PORT)) # ^ hence N-1, sending the newest unsent
        #pkt_list[N-1].time_sent = time.time() # setting time that packet N-1 was sent

  except socket.error, msg: 
    print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit() 

  if pkt_list:        # if pkt_list is not empty (still data being sent)
    time_curr = time.time() # set time
    if time_curr - pkt_list[0].time_sent >= TIMEOUT: # if TIMEOUT has been exceeded
      s.sendto(pkt_list[0].msg, (HOST, PORT)) # idk how to do it for SR
      pkt_list[0].time_sent = time.time()





