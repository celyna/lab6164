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

old_msg = ''
msgList = []
msgList.append("Hello World 1")
msgList.append("Hello World 2")
msgList.append("Hello World 3")
msgList.append("Hello World 4")
msgList.append("Corrupted Hello World 5")
msgList.append("Hello World 6")
msgList.append("Hello World 7")
msgList.append("Hello World 8")
msgList.append("Hello World 9")
msgList.append("Hello World 10")
count = 0
flag = 0
resend = 0

#initializing 
pkt_list = list() #used as list of packets that havent been sent

HOST = 'localhost'
PORT = 2155
BASE = 1      #base for window
PKT = 1       #packet number
N = 4         #window size
TIMEOUT = 10  #timeout time

try: 
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:    
  print 'Failed to create socket' 
  sys.exit() 

while 1: 
  if resend:
    msg = old_msg
    resend = 0
  else:
    msg = raw_input('Enter message to send : jk hardcoded so it doesnt matter ')
    msg = msgList[count]
    old_msg = msg 
    count+=1

  try: # set string
  checksum = ip_checksum(msg)                   #get checksum of message
  if msg[0:1] == 'C' and flag==0:
    checksum = checksum + "c"
    flag = 1
  msg = str(PKT).zfill(3) + str(checksum) + msg #new message: 00PKT+CHKSM+MSG
  pkt_curr = pkt_struct(PKT, msg)               #set current: packet with packet number and msg
  pkt_list.append(pkt_curr) 
  PKT += 1                                      #increment packet number

  
  try:                      #try to send packet
    if (pkt_curr.num < BASE + N):
      pkt_curr.send_pkt(s)  #s.sendto(pkt_curr.msg, (HOST, PORT))
                            #pkt_curr.time_sent = time.time()
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
    if d == '':              #Keep going until server replies with reply
      continue  
    if (reply[3:5] == ip_checksum(reply[5:])) and (BASE == int(reply[0:3])): #dont move window if not sent successfully
      BASE += 1               #move window
      pkt_list.pop(0)         #pop off packetlist bc successful
      #send next packet 
      if len(pkt_list) >= N:      #first N is transfering atm so anything greater than that needs to be sent
        pkt_list[N-1].sent_pkt(s) #s.sendto(pkt_list[N-1].msg, (HOST, PORT)) --> ^ hence N-1, sending the newest unsent
                                  #pkt_list[N-1].time_sent = time.time() --> setting time that packet N-1 was sent
        

  except socket.error, msg: 
    print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit() 

  if pkt_list:        # if pkt_list is not empty (still data being sent)
    time_curr = time.time() # set time
    if time_curr - pkt_list[0].time_sent >= TIMEOUT: # if TIMEOUT has been exceeded
      resend = 1
      s.sendto(pkt_list[0].msg, (HOST, PORT)) #go back and start sending from first unsent
      pkt_list[0].time_sent = time.time()
