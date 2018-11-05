import socket
import sys
import json
import time
from random import randint


LINKS = sys.argv[1].split(',')
TIPOS_MENSAGENS = ['AppendEntries', 'AppendEntriesCommitted', 'UknownIndex', 'RequestVote', 'GiveVote', 'DenyVote', 'Heartbeat','Request']



print('----------------------------------Iniciando Cliente-------------------------------')








def create_msg(type,content):
    return json.dumps({'id': 0,'message-type':type,'content':content,'ip':'0.0.0.0','logIndex': 0})

def sendEverybody(msg):
    for link in LINKS:
        sendRequest(msg,link)


def sendRequest(msg, host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    domain =host.split(':')[0]
    port =int(host.split(':')[1])
    try:
        s.connect((domain, port))
        s.send(msg.encode())
    except ConnectionRefusedError:
        print('Erro ao estabelecer a comunicacao c/ o IP ' + str(host) +':' + str(host))


while(True):
    time.sleep(3)
    numero = str(randint(0,9999999))
    print('Enviando numero '+str(numero)+' para ser escrito')
    sendEverybody(create_msg(TIPOS_MENSAGENS[7],numero))

