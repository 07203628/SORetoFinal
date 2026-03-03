import socket
import ssl
import tkinter as tk
import threading

HOST = '0.0.0.0'
PORT = 5555
AUTH_TOKEN = "clave123"

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def actualizar_interfaz(widget, **kwargs):
    ventana.after(0, lambda: widget.config(**kwargs))
    
def terminar_tarea():
    ventana.after(0, lambda: btn_actualizar.config(state=tk.NORMAL))
    
def iniciar_conexion():
    btn_actualizar.config(state=tk.DISABLED)
    label_alerta.config(text="Conectando...", fg="blue")
    label_datos.config(text="Esperando respuesta del servidor...")    
    hilo = threading.Thread(target=tarea_red, daemon=True)
    hilo.start()

def tarea_red():
    try:
        with socket.create_connection((HOST, PORT), timeout=10) as client_socket:
            with context.wrap_socket(client_socket, server_hostname=HOST) as secure_socket:
                secure_socket.send(AUTH_TOKEN.encode())
                respuesta_auth = secure_socket.recv(1024).decode('utf-8')
                print(f"Respuesta del servidor: {respuesta_auth}")
                
                if "Autenticado" in respuesta_auth:
                    datos_recibidos = secure_socket.recv(1024).decode('utf-8')
                    actualizar_interfaz(label_datos, text=datos_recibidos)
                    actualizar_interfaz(label_alerta, text="Conexión establecida.", fg="green")
                else:
                    actualizar_interfaz(label_datos, text="Autenticación fallida")
                    actualizar_interfaz(label_alerta, text="Acceso denegado", fg="red")
    except Exception as e:
        actualizar_interfaz(label_datos, text="Error de Conexión")
        actualizar_interfaz(label_alerta, text=f"Error: {str(e)}", fg="red")
    finally:
        terminar_tarea()    
        
ventana = tk.Tk()
ventana.title("Monitoreo - Server")
ventana.geometry("450x250")

label_titulo = tk.Label(ventana, text="Monitor de Procesos Distribuidos", font=("Helvetica", 16, "bold"))
label_titulo.pack(pady=15)

label_datos = tk.Label(ventana, text="Presiona el botón para monitorear...", font=("Helvetica", 14))
label_datos.pack(pady=10)

label_alerta = tk.Label(ventana, text="", font=("Helvetica", 12, "bold"))
label_alerta.pack(pady=5)

btn_actualizar = tk.Button(ventana, text="Obtener Estado del Servidor", command=iniciar_conexion, height=2, bg="lightblue")
btn_actualizar.pack(pady=10)

ventana.mainloop()