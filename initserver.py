from resetUrls import getOnliners, addTrojan, addVless, AddToAvailables, generate_base62_password
from main import engine
import json
import requests
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
import base64

def genKeys():
    private_key = x25519.X25519PrivateKey.generate()

    # Получение публичного ключа из приватного
    public_key = private_key.public_key()

    # Сериализация приватного ключа (для сохранения или использования)
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Сериализация публичного ключа
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    private_key_b64 = base64.b64encode(private_key_bytes).decode('utf-8')
    public_key_b64 = base64.b64encode(public_key_bytes).decode('utf-8')

    private_key_b64 = private_key_b64.split('=')[0]
    public_key_b64 = public_key_b64.split('=')[0]

    return private_key_b64, public_key_b64

def addConnection(host, main_port, conport, panel, username, password, remark, site, proto):
    session = requests.session()
    url = f"http://{host}:{main_port}/{panel}/login"
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/add"
    headers = {
        'Accept': 'application/json'
    }
    private, public = genKeys()
    connection = ''
    if proto == "vless":
        connection = {
            "up": 0,
            "down": 0,
            "total": 0,
            "remark": remark,
            "enable": True,
            "expiryTime": 0,
            "listen": "",
            "port": conport,
            "protocol": proto,
            "settings": "{\"clients\": [{\"id\": \"b86c0cdc-8a02-4da4-8693-72ba27005587\",\"flow\": \"\",\"email\": \"first\",\"limitIp\": 0,\"totalGB\": 0,\"expiryTime\": 0,\"enable\": true,\"tgId\": \"\",\"subId\": \"rqv5zw1ydutamcp0\",\"reset\": 0}],\"decryption\": \"none\",\"fallbacks\": []}",
            "streamSettings": "{\"network\": \"tcp\",\"security\": \"reality\",\"externalProxy\": [],\"realitySettings\": {\"show\": false,\"xver\": 0,\"dest\": \"" + site + "\",\"serverNames\": [\"localhost\",\"www.localhost\"],\"privateKey\": \"" + private + "\",\"minClient\": \"\",\"maxClient\": \"\",\"maxTimediff\": 0,\"shortIds\": [\"47595474\",\"7a5e30\",\"810c1efd750030e8\",\"99\",\"9c19c134b8\",\"35fd\",\"2409c639a707b4\",\"c98fc6b39f45\"],\"settings\": {\"publicKey\": \"" + public + "\",\"fingerprint\": \"firefox\",\"serverName\": \"\",\"spiderX\": \"/\"}},\"tcpSettings\": {\"acceptProxyProtocol\": false,\"header\": {\"type\": \"none\"}}}",
            "sniffing": "{\"enabled\": false,\"destOverride\": [\"http\",\"tls\",\"quic\",\"fakedns\"],\"metadataOnly\": false,\"routeOnly\": false}",
            "allocate": "{\"strategy\": \"always\",\"refresh\": 5,\"concurrency\": 3}"
        }
    elif proto == "trojan":
        connection = {
            "up": 0,
            "down": 0,
            "total": 0,
            "remark": remark,
            "enable": True,
            "expiryTime": 0,
            "listen": "",
            "port": conport,
            "protocol": proto,
            "settings": "{\"clients\": [{\"password\": \"" + generate_base62_password() + "\",\"email\": \"firsttrojan\",\"limitIp\": 0,\"totalGB\": 0,\"expiryTime\": 0,\"enable\": true,\"tgId\": \"\",\"subId\": \"rqv5zw1ydutamcp0\",\"reset\": 0}],\"decryption\": \"none\",\"fallbacks\": []}",
            "streamSettings": "{\"network\": \"tcp\",\"security\": \"reality\",\"externalProxy\": [],\"realitySettings\": {\"show\": false,\"xver\": 0,\"dest\": \"" + site + "\",\"serverNames\": [\"localhost\",\"www.localhost\"],\"privateKey\": \"" + private + "\",\"minClient\": \"\",\"maxClient\": \"\",\"maxTimediff\": 0,\"shortIds\": [\"47595474\",\"7a5e30\",\"810c1efd750030e8\",\"99\",\"9c19c134b8\",\"35fd\",\"2409c639a707b4\",\"c98fc6b39f45\"],\"settings\": {\"publicKey\": \"" + public + "\",\"fingerprint\": \"firefox\",\"serverName\": \"\",\"spiderX\": \"/\"}},\"tcpSettings\": {\"acceptProxyProtocol\": false,\"header\": {\"type\": \"none\"}}}",
            "sniffing": "{\"enabled\": false,\"destOverride\": [\"http\",\"tls\",\"quic\",\"fakedns\"],\"metadataOnly\": false,\"routeOnly\": false}",
            "allocate": "{\"strategy\": \"always\",\"refresh\": 5,\"concurrency\": 3}"
        }
    response = session.request("POST", url, headers=headers, data=connection)
    print(response.text)


with open("login.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

    host = lines[0].strip()
    main_port = lines[1].strip()
    panel = lines[2].strip()
    username = lines[3].strip()
    password = lines[4].strip()
    count = int(lines[5].strip())
    proto = lines[6].strip()
    _ = lines[7].strip()
    conport = int(lines[8].strip())
    site = lines[9].strip()
    name = lines[10].strip()

    addConnection(host, main_port, conport, panel, username, password, name, site, proto)

    onliners, inbounds = getOnliners(host, main_port, panel, username, password)
    for indata in inbounds:
        remark = indata['remark']
        id = indata['id']
        if remark.find('trojan') != -1:
            pbk = json.loads(indata['streamSettings'])['realitySettings']['settings']['publicKey']
            sid = json.loads(indata['streamSettings'])['realitySettings']['shortIds'][0]
            for i in range(count):
                key = addTrojan(host,main_port,indata['port'],panel,username,password,id, pbk, sid, remark)
                await AddToAvailables(engine, key)
        elif remark.find('vless') != -1:
            pbk = json.loads(indata['streamSettings'])['realitySettings']['settings']['publicKey']
            sid = json.loads(indata['streamSettings'])['realitySettings']['shortIds'][0]
            for i in range(count):
                key = addVless(host, main_port, indata['port'], panel, username, password, id, pbk, sid, remark)
                await AddToAvailables(engine, key)





