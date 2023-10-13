from PyQt5.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLineEdit, QSizePolicy
from PyQt5.QtGui import QColor, QKeySequence, QFont, QTextCursor
from PyQt5.QtCore import QCoreApplication, Qt
class CommandPromptWindow(QMainWindow):
    def __init__(self, row_id, parent=None):
        self.row_id = row_id
        self.info = parent
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Command Prompt - Row ID {self.row_id}")
        self.setGeometry(100, 100, 600, 400)  # Adjust the window size
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)  # Disable text input
        self.output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Set text color and font
        self.output_box.setTextColor(QColor("white"))
        self.output_box.setFont(QFont("Arial", 9))
        layout.addWidget(self.output_box)
        # Input Box
        self.input_box = QLineEdit()
        layout.addWidget(self.input_box)
        
        # Set a border style for the input box (e.g., a black border)
        self.input_box.setStyleSheet("border: 1px solid blue;")
        
        # Run Button
        self.run_button = QPushButton("Run")
        layout.addWidget(self.run_button)
        
        central_widget.setLayout(layout)
        
        # Set background color to black
        self.setStyleSheet("background-color: black; color: white;")
        
        # Connect the Run button and Enter key press to the same slot
        self.run_button.clicked.connect(self.on_run_button_click)
        self.input_box.returnPressed.connect(self.on_run_button_click)
        self.info.bluepill.send(b"start_cmd", self.info.connection[int(self.row_id) - 1])
        self.input_box.clear()

    def append_text(self, text):
        try:
            self.output_box.append(text)
            # Scroll to the bottom of the text area
            cursor = self.output_box.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.output_box.setTextCursor(cursor)
            self.output_box.ensureCursorVisible()
        except Exception as e:
            print(e)
    def on_run_button_click(self):
        # Get the command from the input box
        command = self.input_box.text()
        if not command:
            return

        if command.lower() in ["clear", "cls"]:
            self.output_box.clear()
            self.input_box.clear()
            return

        self.info.bluepill.send(b'cmd->' + command.encode('utf-8'), self.info.connection[int(self.row_id) - 1])