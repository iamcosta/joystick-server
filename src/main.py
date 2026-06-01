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
        # Actions
        btn_a = False 
        btn_b = False
        btn_x = False
        btn_y = False
        # DPad 
        btn_dpap_up = False
        btn_dpap_right = False
        btn_dpap_down = False
        btn_dpap_left = False
        # Shoulders
        btn_tl = False # LB
        btn_tr = False # RB
        # Special
        btn_select = False # View/Back
        btn_start = False # Menu
        btn_mode = False
        # Stickers
        btn_thumbl = False # LS/L3
        btn_thumbr = False # RS/R3
        try:
            while True:
                # Receive explicit packets and sender properties
                data, addr = server.recvfrom(1024)
                recv_input = data.decode('utf-8')

                # Special
                if "Xbox Menu" in recv_input:
                    btn_start = not btn_start
                    ui.write(e.EV_KEY, e.BTN_START, 1 if btn_start else 0)
                if "Xbox Back" in recv_input:
                    btn_select = not btn_select
                    ui.write(e.EV_KEY, e.BTN_SELECT, 1 if btn_select else 0)

                # Actions
                if "Top Action" in recv_input:
                    btn_y = not btn_y
                    ui.write(e.EV_KEY, e.BTN_Y, 1 if btn_y else 0)
                if "Right Action" in recv_input:
                    btn_b = not btn_b
                    ui.write(e.EV_KEY, e.BTN_B, 1 if btn_b else 0)
                if "Bottom Action" in recv_input:
                    btn_a = not btn_a
                    ui.write(e.EV_KEY, e.BTN_A, 1 if btn_a else 0)
                if "Left Action" in recv_input:
                    btn_x = not btn_x
                    ui.write(e.EV_KEY, e.BTN_X, 1 if btn_x else 0)

                # D Pad
                if "D-pad Up" in recv_input:
                    btn_dpap_up = not btn_dpap_up
                    ui.write(e.EV_ABS, e.ABS_HAT0Y, -1 if btn_dpap_up else 0)
                if "D-pad Right" in recv_input:
                    btn_dpap_right = not btn_dpap_right
                    ui.write(e.EV_ABS, e.ABS_HAT0X, 1 if btn_dpap_right else 0)
                if "D-pad Down" in recv_input:
                    btn_dpap_down = not btn_dpap_down
                    ui.write(e.EV_ABS, e.ABS_HAT0Y, 1 if btn_dpap_down else 0)
                if "D-pad Left" in recv_input:
                    btn_dpap_left = not btn_dpap_left
                    ui.write(e.EV_ABS, e.ABS_HAT0X, -1 if btn_dpap_left else 0)

                # Shoulders
                if "Right Shoulder" in recv_input:
                    btn_tl = not btn_tl
                    ui.write(e.EV_KEY, e.BTN_TR, 1 if btn_tl else 0)
                if "Left Shoulder" in recv_input:
                    btn_tr = not btn_tr
                    ui.write(e.EV_KEY, e.BTN_TL, 1 if btn_tr else 0)
                
                # Stickers
                if "Xbox L/LS" in recv_input:
                    btn_thumbl = not btn_thumbl
                    ui.write(e.EV_KEY, e.BTN_THUMBL, 1 if btn_thumbl else 0)
                if "Xbox R/RS" in recv_input:
                    btn_thumbr = not btn_thumbr
                    ui.write(e.EV_KEY, e.BTN_THUMBR, 1 if btn_thumbr else 0)

                # Triggers
                if "Left Trigger" in recv_input:
                    value = float(recv_input.split("Value")[1])
                    final_value = int(float(1023) * value)
                    ui.write(e.EV_ABS, e.ABS_RZ, final_value)
                if "Right Trigger" in recv_input:
                    value = float(recv_input.split("Value")[1])
                    final_value = int(float(1023) * value)
                    ui.write(e.EV_ABS, e.ABS_Z, final_value)

                # Analog
                if "Left Stick X-Axis" in recv_input:
                    value = float(recv_input.split("Value")[1])
                    final_value = int(float(32767) * value)
                    ui.write(e.EV_ABS, e.ABS_X, final_value)
                if "Left Stick Y-Axis" in recv_input:
                    value = float(recv_input.split("Value")[1])
                    final_value = int(float(32767) * value)
                    ui.write(e.EV_ABS, e.ABS_Y, final_value)
                if "Right Stick X-Axis" in recv_input:
                    value = float(recv_input.split("Value")[1])
                    final_value = int(float(32767) * value)
                    ui.write(e.EV_ABS, e.ABS_RX, final_value)
                if "Right Stick Y-Axis" in recv_input:
                    value = float(recv_input.split("Value")[1])
                    final_value = int(float(32767) * value)
                    ui.write(e.EV_ABS, e.ABS_RY, final_value)
                
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