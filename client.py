import socket
import threading
import queue
import base64
import hashlib
import time
import sys


def send_respond(mess):

    # Envio de data
    print('Enviando {!r}'.format(mess))
    sock.sendall(mess)

    while True:
        data = sock.recv(21)
        print('Recibido {!r}'.format(data))

        if (data.decode().startswith('ok') == False):
            print('Error recibido')
            sock.close()
            sock_udp.close()
            ciclo.put(True)
            sys.exit()
        break
    return data

# def udp_server(port):
    # Create a UDP socket
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # # Bind the socket to the port
    # server_address = ('127.0.0.1', port)
    # print('starting up on {} port {}'.format(*server_address))
    # sock.bind(server_address)

    # while True:
    #     print('\nwaiting to receive message')
    #     data, address = sock.recvfrom(4096)

    #     print('received {} bytes from {}'.format(
    #         len(data), address))
    #     print(data)

    #     if data:
    #         sent = sock.sendto(data, address)
    #         print('sent {} bytes back to {}'.format(
    #             sent, address))


def udp_server(port, cola, ciclo):

    clientMsg = ''
    # Creacion de socket
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind(('0.0.0.0',port))
    print("Servidor UDP escuchando...")

    # Listening
    while(True):
        if ciclo.get():
            print('Servidor UDP finalizo')
            break
        bytesAddressPair = UDPServerSocket.recvfrom(12000)
        message = bytesAddressPair[0]
        cola.put(message)

            
# Creacion del TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Ingrese una direccion IP  o localhost \n')
ip = input('IP = ')
porttcp = int(input('Puerto = '))

# Conexion al puerto
server_address = (ip, porttcp)
print('Conectando a {} puerto {}'.format(*server_address))
sock.connect(server_address)

threads = []
cola = queue.Queue()
ciclo = queue.Queue()
try:

    # Introduccion del usuario
    username = input('Usuario = ')
    print('\n')
    messagef = 'helloiam' + ' ' + username
    send_respond(messagef.encode())

    msglen = 'msglen'
    send_respond(msglen.encode())

    give = 'givememsg'
    port = input('Puerto UDP = ').encode()
    givemsg = give + ' ' + port.decode()

    ciclo.put(False)
    server = threading.Thread(target=udp_server, args=(int(port),cola,ciclo))
    threads.append(server)
    server.start()
    f = send_respond(givemsg.encode())
    
    intentos = 0
   
    while (intentos < 7):
        if cola.empty() == False:
            try:
                tmp = cola.get(block=False)
                if tmp:
                    # print('Existe respuesta')
                    value = tmp.decode()
                    break
                else:
                    print('No existe respuesta')
                print(f'Value = {value}')
            except:
                print('Cola vacia')
        else:
            time.sleep(3)
            print(f'Mensaje no recibido, reintentando...{intentos}')
            f = send_respond(givemsg.encode())
            intentos += 1

    if (intentos >= 7):
        print('Lo siento, no se ha recibido ningun mensaje')
        sock.close()
        sock_udp.close()
        ciclo.put(True)
    else:
        aux2 = base64.b64decode(value)
        print('\n')
        print(f'El mensaje = {aux2.decode()}')
        aux3 = hashlib.md5(aux2)
        auxf = aux3.hexdigest()
        # print(f'Value = {auxf}')

        check = 'chkmsg' + ' ' + str(auxf)
        send_respond(check.encode())
        send_respond('bye'.encode())
    

except ConnectionAbortedError:
    print('Conexion perdida con el servidor')
except ValueError:
    print('EL puerto debe ser un numero')
except TimeoutError:
    print('La conexion no se pudo establecer')
except OverflowError:
    print('El puerto es invalido')
finally:
    print('Closing sockets')
    sock.close()
    sock_udp.close()
    ciclo.put(True)