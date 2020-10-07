import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json

clients_lock = threading.Lock()
connected = 0

clients = {}

def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      data = str(data)
      print(data)
      data = data [2 : len(data) -1]
      print(data)
      data = json.loads(data)
      if addr in clients:
         if 'heartbeat' in data["cmd"]:
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]
         if 'updateposition' in data["cmd"]:
            clients[addr]['posX'] = data["X"]
            clients[addr]['posY'] = data["Y"]
            clients[addr]['posZ'] = data["Z"]   
      else:
         if 'connect' in data["cmd"]:
            clients[addr] = {}
            clients[addr]['lastBeat'] = datetime.now()
            clients[addr]['color'] = 0
            clients[addr]['posX'] = random.uniform(-5,5)
            clients[addr]['posY'] = random.uniform(-5,5)
            clients[addr]['posZ'] = random.uniform(-5,5)
            message = {"cmd": 0,"id":str(addr)}
            m2 = json.dumps(message)
            for c in clients:
               sock.sendto(bytes(m2,'utf8'), (c[0],c[1]))
            pMessage = {"cmd": 3,"id":str(addr)}
            m = json.dumps(pMessage)
            sock.sendto(bytes(m,'utf8'), (addr[0],addr[1]))

def cleanClients(sock):
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            message = {"cmd": 2,"id":str(c)}
            m = json.dumps(message)
            for c2 in clients:
               sock.sendto(bytes(m,'utf8'), (c2[0],c2[1]))
            del clients[c]
            clients_lock.release()
      time.sleep(1)

def gameLoop(sock):
   while True:
      GameState = {"cmd": 1, "players": []}
      clients_lock.acquire()
      print (clients)
      for c in clients:
         player = {}
         clients[c]['color'] = {"R": random.random(), "G": random.random(), "B": random.random()}
         player['id'] = str(c)
         ##player['pos'] = {"X": clients[c].position.x, "Y": clients[c].position.y, "Z": clients[c].position.z}
         player['color'] = clients[c]['color']
         player['posX'] = clients[c]['posX']
         player['posY'] = clients[c]['posY']
         player['posZ'] = clients[c]['posZ']
         GameState['players'].append(player)
      s=json.dumps(GameState)
      print(s)
      for c in clients:
         sock.sendto(bytes(s,'utf8'), (c[0],c[1]))
      clients_lock.release()
      time.sleep(1)

def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(gameLoop, (s,))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(cleanClients,(s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()
