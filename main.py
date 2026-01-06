import cv2
import socket
import pickle
import struct
from zeroconf import ServiceInfo, Zeroconf

# Configuración de Red
SERVER_PORT = 5005
zc = Zeroconf()
info = ServiceInfo(
    "_camera._tcp.local.",
    "AndroidCam._camera._tcp.local.",
    addresses=[socket.inet_aton("0.0.0.0")],
    port=SERVER_PORT,
    properties={'device': 'Android'},
)

def start_sender():
    zc.register_service(info)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Ajustamos el tamaño del buffer para video
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000)
    
    cap = cv2.VideoCapture(0) # Cámara del móvil
    
    print("Transmitiendo... Buscando receptor.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            # Reducir tamaño para optimizar ancho de banda
            frame = cv2.resize(frame, (640, 480))
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            
            # Enviamos a la dirección de broadcast o específica si se conoce
            # Por simplicidad aquí enviamos a broadcast de la subred
            client_socket.sendto(buffer, ('<broadcast>', SERVER_PORT))
            
    finally:
        zc.unregister_service(info)
        zc.close()
        cap.release()

if __name__ == "__main__":
    start_sender()
