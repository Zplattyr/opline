import socket

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

def start_server(ADDR):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR)
    server_socket.listen(5)
    print(f"Сервер запущен на {ADDR}, ожидаем соединения...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Подключен клиент: {client_address}")

        while True:
            message = client_socket.recv(1024).decode('utf-8')

            if not message:
                break
            print(f"Сообщение от клиента: {message}")

            response = f"Эхо: {message}"
            client_socket.send(response.encode('utf-8'))

        client_socket.close()
        print(f"Отключен клиент: {client_address}")


if __name__ == "__main__":
    start_server(ADDR)


a='trojan://yGWeXaIkVe@185.70.196.100:33218?type=tcp&security=reality&pbk=69pnj67jNdT_r4DOusldu0YAbGp69rMJK4dM_4NWEgc&fp=random&sni=yahoo.com&sid=08aaa9fc6b3c&spx=%2F#poland-1-trojan-969d9816-9e5d-11ef-bf21-00155d968f58'
b='trojan://yGWeXaIkVe@185.70.196.100:33218?type=tcp&security=reality&pbk=69pnj67jNdT_r4DOusldu0YAbGp69rMJK4dM_4NWEgc&fp=random&sni=yahoo.com&sid=08aaa9fc6b3c&spx=%2F#poland-1-trojan-969d9816-9e5d-11ef-bf21-00155d968f58'