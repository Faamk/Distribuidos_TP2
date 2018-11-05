import asyncio
import json
import socket
import sys


STATUS_POSSIVEIS = ['LEADER','FOLLOWER','CANDIDATE']
TIPOS_MENSAGENS = ['AppendEntries', 'AppendEntriesCommitted', 'UknownIndex', 'RequestVote', 'GiveVote', 'DenyVote', 'Heartbeat','Request']
LINK = sys.argv[1]
LINKS = sys.argv[2].split(',')
ID = sys.argv[3]
ID_LIDER = 0
status = STATUS_POSSIVEIS[2]
contado = 0
contador_max=5
votos = 0
votos_max = 2
confirmations = 0
confirmations_max = 2
log = open(sys.argv[4],'a')
lastThing = ''







print('----------------------------------Iniciando Nodo Raft-------------------------------')


def getIndex():
    try:
        lines = open(sys.argv[4],'r').read().splitlines()
        last_line = lines[-1]
        lastLine = last_line[:5]
        return int(lastLine)
    except IndexError:
        return 0



index = getIndex()

def create_msg(type,content,index):
    return json.dumps({'id': ID,'message-type':type,'content':content,'ip':LINK,'logIndex':index})


async def sendVoteRequest():
    await sendEverybody(create_msg(TIPOS_MENSAGENS[3], '',index))


def getLogIndex(index):
    lines = open(sys.argv[4],'r').read().splitlines()
    return lines[index-1][8:]


async def sendHeartbeat():
    await sendEverybody(create_msg(TIPOS_MENSAGENS[0], getLogIndex(index),index))


async def add_time():
    print (status)
    while True:
        if status != STATUS_POSSIVEIS[0]:
            await asyncio.sleep(1)
            global contado
            global contador_max
            global votos
            contado = contado+1
            print('tempo restante para Timeout: '+str(contado))
            if contado==contador_max:
                print('Requisitando Votacao para lider')
                votos = 0
                await sendVoteRequest()
                contado = 0
        else:
            await asyncio.sleep(1)
            print('Heartbeat')
            await sendHeartbeat()



async def sendRequest(msg, host):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    domain =host.split(':')[0]
    port =int(host.split(':')[1])
    try:
        s.connect((domain, port))
        s.send(msg.encode())
    except ConnectionRefusedError:
        print('Erro ao estabelecer a comunicacao c/ o IP ' + str(host) +':' + str(host))


async def contador():
    await asyncio.sleep(1)
    bob = contado




async def sendEverybody(msg):
    for link in LINKS:
        await sendRequest(msg,link)


def writelog(msg):
    global index
    index += 1
    log.write("{0:0=5d}".format(index)+' - '+msg+'\n')
    log.flush()


async def sendLog(msg,content):
    writelog(content)
    await sendEverybody(msg)


async def checkIfWin():
    global status
    global ID_LIDER
    global votos
    global contado

    if votos >= votos_max:
        status = STATUS_POSSIVEIS[0]
        ID_LIDER = ID
        print('FUI ELEITO' + str(status))
        await sendLog(create_msg(TIPOS_MENSAGENS[0],'Nodo '+str(ID)+' - Eleito Lider',index),'Nodo '+str(ID)+' - Eleito Lider')
        votos = 0
        contado = 0



async def denyvote(ip):
    print('NAO votei em '+str(ip)+' para lider')
    await sendRequest(create_msg(TIPOS_MENSAGENS[5], '',index),ip)


async def giveVote(ip):
    print('votei em '+str(ip)+' para lider')
    await  sendRequest(create_msg(TIPOS_MENSAGENS[4], '',index),ip)


def commitChanges():
    pass


async def handle_client(reader, writer):
    request = (await reader.read(255)).decode('utf8')
    joso = json.loads(request)
    global contado
    global votos
    global status
    global confirmations

    if joso['message-type'] == TIPOS_MENSAGENS[7] and status == STATUS_POSSIVEIS[0]:
        print('Msg do cliente recebida!')
        await sendLog(create_msg(TIPOS_MENSAGENS[0],'Msg do Cliente - ' + joso['content'],index),'Msg do Cliente - ' + joso['content'])





    if   joso['message-type']==TIPOS_MENSAGENS[6]:
        print('Heartbeat Recebido')
        contado=0;
    elif joso['message-type']==TIPOS_MENSAGENS[5]:
        pass
    elif joso['message-type']==TIPOS_MENSAGENS[4]:
        if status == STATUS_POSSIVEIS[2]:
            print('Recebi voto de '+str(joso['ip']))
            votos+=1
            await checkIfWin()
    elif joso['message-type']==TIPOS_MENSAGENS[3]:
        print ('votos:'+str(votos))
        if status == STATUS_POSSIVEIS[0]:
            await denyvote(joso['ip'])
            contado=0
        else:
            status = STATUS_POSSIVEIS[2]
            await giveVote(joso['ip'])
            contado=0
            votos = 0


    elif joso['message-type']==TIPOS_MENSAGENS[2]:
        await sendRequest(create_msg(TIPOS_MENSAGENS[0],getLogIndex(int(joso['logIndex'])-1),int(joso['logIndex'])-1),joso['ip'])

    elif joso['message-type'] == TIPOS_MENSAGENS[1]:
        if(joso['logIndex']==index):
            confirmations+=1
            if confirmations>=confirmations_max:
                confirmations=0
                commitChanges()


    elif joso['message-type'] == TIPOS_MENSAGENS[0]:
        print(joso)
        print('Meu index - '+str(index))
        contado=0;
        if(int(joso['logIndex'])-1>index):
            print('Detectado Indice de log - '+str(joso['logIndex'])+' - maior q o meu : '+str(index))
            await sendRequest(create_msg(TIPOS_MENSAGENS[2],joso['content'],int(joso['logIndex'])),joso['ip'])
        elif(int(joso['logIndex'])-1==index):
            writelog(joso['content'])
            await sendRequest(create_msg(TIPOS_MENSAGENS[1],joso['content'],index),joso['ip'])


loop = asyncio.get_event_loop()
print("vou tentar entrar no socket"+' localhost' +str(LINK.split(':')[1]))
loop.create_task(asyncio.start_server(handle_client, '0.0.0.0', LINK.split(':')[1]))
loop.create_task(add_time())
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()