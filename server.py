import socket
import ssl
import psutil

def main():
    HOST = '0.0.0.0'
    PORT = 5555
    
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Prevents "Address already in use"
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"[*] Servidor seguro escuchando en {HOST}:{PORT}...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"[*] Conexión entrante de {addr}")
            
        try:
            with context.wrap_socket(client_socket, server_side=True) as secure_socket:        
                token = secure_socket.recv(1024).decode()
                
                if token == "clave123":
                    secure_socket.send("Autenticado. Enviando datos...".encode())
                    cpu = psutil.cpu_percent(interval=1)
                    ram = psutil.virtual_memory().percent
                    datos = f"CPU: {cpu}% | RAM: {ram}%"
                    secure_socket.send(datos.encode())
                else:
                    secure_socket.send("Acceso denegado.".encode())
        
        except ssl.SSLError as e:
            print(f"[!] Error SSL (Handshake fallido): {e}")
        except Exception as e:
            print(f"[!] Error general con el cliente {addr}: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    main()