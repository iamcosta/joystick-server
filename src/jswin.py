import socket
import pyvjoystick.vigem as vg

HOST = "192.168.100.8"
DEFAULT_PORT = 65432

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
    
axisLX = float(0)
axisLY = float(0)
axisRX = float(0)
axisRY = float(0)

def joystick_control(server: socket):
    gp = vg.VX360Gamepad()
    XBUTTON_MAPPER = {
        "304": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        "305": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        "307": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        "308": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        "315": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        "314": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        "317": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        "318": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        "310": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        "311": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        "DPU": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        "DPD": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        "DPL": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        "DPR": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
    }
    try:
        while True:
            # Receive explicit packets and sender properties
            data, addr = server.recvfrom(1024)
            recv_input: str = data.decode('utf-8')
            if ":" in recv_input:
                data_members = recv_input.split(":")
                if data_members[0] == "BTN":
                    if data_members[2] == "1":
                        gp.press_button(button=XBUTTON_MAPPER[data_members[1]])
                    elif data_members[2] == "0":
                        gp.release_button(button=XBUTTON_MAPPER[data_members[1]])
                if data_members[0] == "AXIS":
                    if data_members[1] == "17":
                        if data_members[2] == "-1":
                            gp.press_button(button=XBUTTON_MAPPER["DPU"])
                        elif data_members[2] == "1":
                            gp.press_button(button=XBUTTON_MAPPER["DPD"])
                        else:
                            gp.release_button(button=XBUTTON_MAPPER["DPU"])
                            gp.release_button(button=XBUTTON_MAPPER["DPD"])
                    if data_members[1] == "16":
                        if data_members[2] == "-1":
                            gp.press_button(button=XBUTTON_MAPPER["DPL"])
                        elif data_members[2] == "1":
                            gp.press_button(button=XBUTTON_MAPPER["DPR"])
                        else:
                            gp.release_button(button=XBUTTON_MAPPER["DPL"])
                            gp.release_button(button=XBUTTON_MAPPER["DPR"])
                if data_members[1] == "2":
                    gp.left_trigger_float(float(data_members[2]) / 1023)
                if data_members[1] == "5":
                    gp.right_trigger_float(float(data_members[2]) / 1023)
                if data_members[1] == "0":
                    global axisLX
                    axisLX = float(data_members[2]) / 32767
                if data_members[1] == "1":
                    global axisLY
                    axisLY = float(data_members[2]) / 32767
                if data_members[1] == "3":
                    global axisRX
                    axisRX = float(data_members[2]) / 32767
                if data_members[1] == "4":
                    global axisRY
                    axisRY = float(data_members[2]) / 32767
                gp.left_joystick_float(x_value_float=axisLX, y_value_float=axisLY)
                gp.right_joystick_float(x_value_float=axisRX, y_value_float=axisRY)
                gp.update()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server.close()

def run_app():
    server = create_server()
    joystick_control(server)
        

if __name__ == "__main__":
    run_app()