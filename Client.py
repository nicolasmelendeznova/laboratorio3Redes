import datetime
import socket
import hashlib
import threading
import logging
import time

SIZE=1024

FOLDER="ArchivosRecibidos/"

port = 4456 

def hash_file(f):
    hash_object = hashlib.md5()
    hash_object.update(f)
    return hash_object.hexdigest()


def save_file(id, data):
    file = open('Cliente'+FOLDER+id+'-Prueba-'+str(clients)+'.txt', "wb")
    file.write(data)

def log(message, error=False):
    if not error:
        logging.info(message)
    else:
        logging.error(message)

while True:

    host = socket.gethostname()
    host = socket.gethostbyname(host + ".local")

    global clients
    clients = int(input("Numero de clientes a enviar:"))

    def connect_client():

        def send(message):
            connection.send(message.encode(encoding='ascii', errors='ignore'))

        def receive():
            return connection.recv(SIZE).decode(encoding="ascii", errors="ignore")

        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((host, port)) 
        print("Conecto")
        print("Esperando la conexion")

        id = receive()
        log('Client number: '+id+' connected to the server')
        print('Confirmation received id:', id)

        received_hash_code = receive()
        print('Client '+id+ ' - hash received:', received_hash_code)
  
        send('Client '+id+ ' - Hash received')

        start_time = time.time()
        data = connection.recv(SIZE)
        generated_hash_code = hash_file(data)

        if received_hash_code != generated_hash_code:
            print('Client '+id+ ' - Received file is corrupted')
            print('Client '+id+ ' - Hash received:', received_hash_code)
            print('Client '+id+ ' - Hash generated:', generated_hash_code)
            send('Received file is corrupted') 
            log('Client '+id+' received a corrupt file', True)
        else:
            log('File successfully received by client '+id)
            print('Client '+id+ ' - File received')
            send('Nice') 
        total_time = time.time() 
        log('Total transference time for client '+id+':'+str(total_time))
        
        save_file(id, data)
        connection.close()

    threads = []
    op = True
    for i in range(clients):
        thread = threading.Thread(target=connect_client)
        thread.start()
        threads.append(thread)
    now = datetime.datetime.now()
    log_path = './log/client/'+ str(now.year) +'-'+ str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'-log.txt'
       
    logging.basicConfig(level=logging.INFO, filename=log_path, filemode='w', format='%(asctime)s - %(message)s')
            
    for t in threads:
        t.join()
