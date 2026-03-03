import socket
import ssl
import psutil
import threading

HOST = '0.0.0.0'
PORT = 5555
AUTH_TOKEN = "clave123"

def manejar_cliente(client_socket, addr, context):
    try: 
        with context.wrap_socket(client_socket, server_side=True) as secure_socket:        
            token = secure_socket.recv(1024).decode('utf-8').strip()   
            
            if token  == AUTH_TOKEN:
                secure_socket.send("Autenticado. Enviando datos...".encode())
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                datos = f"CPU: {cpu}% | RAM: {ram}%"
                secure_socket.send(datos.encode('utf-8'))
                print(f"> Datos enviados a {addr}")
            else:
                secure_socket.send("Acceso denegado.".encode('utf-8'))
                print(f"> Acceso denegado para {addr}: Token incorrecto '{token}'")
    except ssl.SSLError as e:
        print(f"> Error SSL con {addr}: {e}")
    except Exception as e:
        print(f"> Error general con {addr}: {e}")
    finally:
        client_socket.close()
        print(f"> Conexión cerrada con {addr}")
    
    print(f"> Servidor seguro escuchando en {HOST}:{PORT}...")
    
def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    try:
        context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    except FileNotFoundError:
        print("> Error: No se encontraron 'server.crt' y 'server.key'.")
        return
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"> Servidor seguro escuchando en {HOST}:{PORT}...")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"> Conexión entrante de {addr}")
            
            hilo_cliente = threading.Thread(
                target=manejar_cliente,
                args=(client_socket, addr, context),
                daemon=True
            )
            hilo_cliente.start()
    except KeyboardInterrupt:
        print(">Servidor detenido por el usuario.")
    finally:
        server_socket.close()
        print("> Servidor cerrado.")
        
if __name__ == "__main__":
    main()