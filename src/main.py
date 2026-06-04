import socket
from evdev import UInput, ecodes as e

HOST = "192.168.100.8"
DEFAULT_PORT = 65432
JS_BTN = [
    e.BTN_SOUTH,   # Botão A
    e.BTN_EAST,    # Botão B
    e.BTN_NORTH,   # Botão X
    e.BTN_WEST,    # Botão Y
    e.BTN_TL,      # Shoulder Esquerdo (LB)
    e.BTN_TR,      # Shoulder Direito (RB)
    e.BTN_SELECT,  # Botão Back / View
    e.BTN_START,   # Botão Start / Menu
    e.BTN_MODE,    # Botão Logo Xbox (Home)
    e.BTN_THUMBL,  # Clique no Analógico Esquerdo (LS)
    e.BTN_THUMBR,  # Clique no Analógico Direito (RS)
    e.BTN_MODE,    # Botão Logo Xbox (Home)
]
JS_AXIS = {
    e.ABS_X: (0, -32768, 32767, 16, 128),      # Analógico Esquerdo - Horizontal
    e.ABS_Y: (0, -32768, 32767, 16, 128),      # Analógico Esquerdo - Vertical
    e.ABS_RX: (0, -32768, 32767, 16, 128),     # Analógico Direito - Horizontal
    e.ABS_RY: (0, -32768, 32767, 16, 128),     # Analógico Direito - Vertical
    e.ABS_Z: (0, 0, 1023, 4, 16, 16),               # Gatilho Esquerdo (LT)
    e.ABS_RZ: (0, 0, 1023, 4, 16, 16),              # Gatilho Direito (RT)
    e.ABS_HAT0X: (0, -1, 1),                   # D-Pad - Horizontal (Esquerda/Direita)
    e.ABS_HAT0Y: (0, -1, 1),                   # D-Pad - Vertical (Cima/Baixo)
}

def create_server(host: str = HOST, port: int = DEFAULT_PORT) -> socket:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((host, port))
        print(f"Server succesfully started on {HOST}:{DEFAULT_PORT}")
        return server
    except:
        print("Failed to start server")
        raise Exception("Failed to start server")

def close_server(server: socket):
    server.close()
    print("Server closed")
    
def joystick_control(server: socket):
    with UInput(events={e.EV_KEY: JS_BTN, e.EV_ABS: JS_AXIS}, name="Microsoft X-Box 360", vendor=0x045e, product=0x028e, version=0x0110) as ui:
        try:
            while True:
                # Receive explicit packets and sender properties
                data, addr = server.recvfrom(1024)
                recv_input: str = data.decode('utf-8')
                if ":" in recv_input:
                    data_members = recv_input.split(":")
                    if data_members[0] == "BTN":
                        ui.write(e.EV_KEY, int(data_members[1]), int(data_members[2]))
                    if data_members[0] == "AXIS":
                        ui.write(e.EV_ABS, int(data_members[1]), int(float(data_members[2])))
                    ui.syn()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            server.close()

def run_app():
    server = create_server()
    joystick_control(server)
        

if __name__ == "__main__":
    run_app()