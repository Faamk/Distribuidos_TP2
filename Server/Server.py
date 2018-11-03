import asyncio
import json
import socket


STATUS_POSSIVEIS = ['LEADER','FOLLOWER','CANDIDATE']
TIPOS_MENSAGENS = ['AppendEntries', 'AppendEntriesCommitted', 'AcceptAppendEntries', 'RequestVote', 'GiveVote', 'DenyVote', 'Heartbeat']
LINK = 15555
LINKS = [15556,15557]
ID = 1
ID_LIDER = 0
status = STATUS_POSSIVEIS[2]
contado = 0
contador_max=5
votos = 0
votos_max = 2


print('----------------------------------Iniciando Nodo Raft-------------------------------')




def create_msg(type,content):
    return json.dumps({'id': ID,'message-type':type,'content':content,'ip':LINK})


async def sendVoteRequest():
    await sendEverybody(create_msg(TIPOS_MENSAGENS[3], ''))

async def sendHeartbeat():
    await sendEverybody(create_msg(TIPOS_MENSAGENS[6], ''))


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
                print('Requisitando Votação para líder')
                votos = 0
                await sendVoteRequest()
                contado = 0
        else:
            await asyncio.sleep(1)
            print('Heartbeat')
            await sendHeartbeat()



async def sendRequest(msg,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host ="localhost"
    port =port
    try:
        s.connect((host,port))
        s.send(msg.encode())
    except ConnectionRefusedError:
        print('Erro ao estabelecer a comunicação c/ o IP '+str(host)+':'+str(port))


async def contador():
    await asyncio.sleep(1)
    bob = contado




async def sendEverybody(msg):
    for link in LINKS:
        await sendRequest(msg,link)


def checkIfWin():
    global status
    global ID_LIDER
    global votos
    global contado

    if votos >= votos_max:
        status = STATUS_POSSIVEIS[0]
        ID_LIDER = ID
        print('FUI ELEITO' + str(status))
        votos = 0
        contado = 0



async def denyvote(ip):
    print('NÃO votei em '+str(ip)+' para líder')
    await sendRequest(create_msg(TIPOS_MENSAGENS[5], ''),ip)


async def giveVote(ip):
    print('votei em '+str(ip)+' para líder')
    await  sendRequest(create_msg(TIPOS_MENSAGENS[4], ''),ip)


async def handle_client(reader, writer):
    request = (await reader.read(255)).decode('utf8')
    joso = json.loads(request)
    global contado
    global votos
    global status

    if   joso['message-type']==TIPOS_MENSAGENS[6]:
        contado=0;
    elif joso['message-type']==TIPOS_MENSAGENS[5]:
        pass
    elif joso['message-type']==TIPOS_MENSAGENS[4]:
        if status == STATUS_POSSIVEIS[2]:
            print('Recebi voto de '+str(joso['ip']))
            votos+=1
            checkIfWin()
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
        contado=0;

    elif joso['message-type'] == TIPOS_MENSAGENS[1]:
        contado=0;

    elif joso['message-type'] == TIPOS_MENSAGENS[0]:
        print('Heartbeat Recebido')
        contado=0;


loop = asyncio.get_event_loop()
loop.create_task(asyncio.start_server(handle_client, 'localhost', LINK))
loop.create_task(add_time())
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()