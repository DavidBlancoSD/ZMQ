"""Tres en NaN"""

import argparse
import os
from threading import Thread
#from future import pintartablero

from netifaces import interfaces, ifaddresses, AF_INET # dependency, not in stdlib

import zmq

def victoria(jugador, tablero):
        #jugador(1 o 2) tablero(diccionario)
        if (tablero.get(1)==tablero.get(2)==tablero.get(3)==jugador or 
        tablero.get(4)==tablero.get(5)==tablero.get(6)==jugador or 
        tablero.get(7)==tablero.get(8)==tablero.get(9)==jugador or
        tablero.get(1)==tablero.get(4)==tablero.get(7)==jugador or
        tablero.get(2)==tablero.get(5)==tablero.get(8)==jugador or
        tablero.get(3)==tablero.get(6)==tablero.get(9)==jugador or
        tablero.get(1)==tablero.get(5)==tablero.get(9)==jugador or
        tablero.get(7)==tablero.get(5)==tablero.get(3)==jugador):
                return True
        else:
                return False

def pintartablero(diccionario):
    for x in range(1,3):
        for y in range(1,3):
            #sys.stdout.write("...")
            print ("||" + diccionario[x+y-1] + "||", os.linesep())
        print() 
    print("Inserte nueva jugada:")

def listen(masked):
    """listen for messages
    
    masked is the first three parts of an IP address:
    
        192.168.1
    
    The socket will connect to all of X.Y.Z.{1-254}.
    """
    posicion=1
    ctx = zmq.Context.instance()
    listener = ctx.socket(zmq.SUB)
    for last in range(1, 255):
        listener.connect("tcp://{0}.{1}:9000".format(masked, last))
    
    listener.setsockopt(zmq.SUBSCRIBE, b'')
    print("Bienvenidos a tres en NaN")
    while victoria(2, diccionario):
        try:
            diccionario=listener.recv();
            pintartablero(diccionario)
            posicion=raw_input()
            while diccionario[posicion]!=0:
                print("Esa posicion ya esta ocupada, elige otra:")
                posicion=raw_input()
            diccionario[posicion]=2
            msg=diccionario
            listener.send(msg)
        except (KeyboardInterrupt, zmq.ContextTerminated):
            break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("interface", type=str, help="the network interface",
        choices=interfaces(),
    )
    parser.add_argument("user", type=str, default="olakase",
        nargs='?',
        help="Your username",
    )
    args = parser.parse_args()
    inet = ifaddresses(args.interface)[AF_INET]
    addr = inet[0]['addr']
    masked = addr.rsplit('.', 1)[0]
    
    ctx = zmq.Context.instance()
    
    listen_thread = Thread(target=listen, args=(masked,))
    listen_thread.start()
    
    posicion=1
    empezar=1
    diccionario={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}
    bcast = ctx.socket(zmq.PUB)
    bcast.bind("tcp://%s:9000" % args.interface)
    print("Bienvenidos a Tres en NaN")
    while victoria(1, diccionario):
        try:
            if empezar==0:
                diccionario=bcast.recv()    
            pintartablero(diccionario)
            posicion=raw_input()
            diccionario[posicion]=1
            msg=diccionario
            bcast.send(msg)
            if empezar==1:
                empezar=0;
        except KeyboardInterrupt:
            break
    bcast.close(linger=0)
    ctx.term()

if __name__ == '__main__':
    main()
