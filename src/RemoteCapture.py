from PyQt5.QtWidgets import (
    QMainWindow, 
    QApplication, 
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QPushButton, 
    QHBoxLayout, 
    QLineEdit,
    QSpinBox,
    QSpacerItem,
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage, QMouseEvent,QKeyEvent, QColor
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import mss
import threading
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QMenu
import pickle
import base64
import json
class ImageLabelUpdateEvent(QObject):
    imageUpdated = pyqtSignal(QPixmap)

class CustomQLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.info = self.parent()
        try: self.display = json.loads(self.info.display_data)
        except: self.display = self.info.display_data
        self.setFocusPolicy(Qt.StrongFocus)  # Set the focus policy to enable keyboard input
        self.user_id = self.info.window
        self.position = 0
        self.keys = {b"shift": 16777248, b"ctrl": 16777249, b"capslock": 16777252, b"esc": 16777216, b"alt": 16777251, b"cmd": 16777250, b"enter": 16777220, b"backspace": 16777219, b"up": 16777235, b"left": 16777234, b"down":16777237, b"right": 16777236}

    def keyPressEvent(self, event):
        key = event.key()
        try:text = ord(event.text())
        except: text = None
        if key > 256:
            for name, value in self.keys.items():
                if value == key: self.info.my_window.bluepill.send(b"keyboard->" + name, self.info.my_window.connection[self.info.window])
            return
        else: 
            if text: self.info.my_window.bluepill.send(b"keyboard->" + str(text).encode('utf-8'), self.info.my_window.connection[int(self.info.window) - 1])
    def mouseMoveEvent(self, event: QMouseEvent):
        label = self.info.image_label
        original_width = label.pixmap().width() - 1
        original_height = label.pixmap().height() - 1
        x = event.x()
        y = event.y()
        dimention = self.display[self.info.monitor]['size']
        target_width = dimention['Item1']
        target_height = dimention['Item2']
        x_scale = target_width / original_width
        y_scale = target_height / original_height
        new_x = int(x * x_scale) + self.get_pos()
        new_y = int(y * y_scale) + int(self.display[self.info.monitor]['position']['Item2'])
        self.info.my_window.bluepill.send(b"mouse->" + (str(new_x) + " " + str(new_y)).encode('utf-8'), self.info.my_window.connection[self.info.window])
        self.position = 0
    def get_pos(self) -> int:
        for i in range(self.info.monitor):
            self.position += self.display[i]['resolution']['Item1']
        return self.position
    
    def mousePressEvent(self, event: QMouseEvent):
        self.info.my_window.bluepill.send(b"input->" + str(event.button()).encode('utf-8'), self.info.my_window.connection[self.info.window])
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.info.my_window.bluepill.send(b"input->" + str(event.button()).encode('utf-8'), self.info.my_window.connection[self.info.window])

class ScreenshotWindow(QWidget):
    def __init__(self, window_name: str, display: dict, parent=None):
        self.window = int(window_name) - 1
        self.display_data = display
        self.my_window = parent
        self.active_stream = True
        
        self.monitor = 0
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a QVBoxLayout to hold the QLabel widget and other widgets
        layout = QVBoxLayout(self)

        # Create a QLabel widget to display the screenshot
        self.image_label = CustomQLabel(self)
        layout.addWidget(self.image_label)
        self.client_monitors = self.image_label.display[self.window]['len_monitors'] - 1
        print(self.client_monitors)
        # Create a QHBoxLayout to hold the number spinner and submit button
        input_layout = QHBoxLayout()

        # Create a QSpinBox for numeric input
        self.number_spinner = QSpinBox(self)
        self.number_spinner.setMinimum(1)  # Set minimum value
        self.number_spinner.setMaximum(100)  # Set maximum value
        input_layout.addWidget(self.number_spinner)

        # Create a QPushButton
        self.button = QPushButton("Quality", self)
        input_layout.addWidget(self.button)

        # Add a "Next Monitor" button
        
        self.previous_monitor_button = QPushButton("Previous Monitor", self)
        input_layout.addWidget(self.previous_monitor_button)

        # Add a "Previous Monitor" button
        self.next_monitor_button = QPushButton("Next Monitor", self)
        input_layout.addWidget(self.next_monitor_button)

        # Set MouseTracking property of the button to False
        self.button.setMouseTracking(False)

        # Add input_layout to the main layout
        layout.addLayout(input_layout)

        # Connect the button's click event to a slot
        self.button.clicked.connect(self.handle_button_click)

        # Connect the signal to a slot
        self.imageUpdateSignal = ImageLabelUpdateEvent()
        self.imageUpdateSignal.imageUpdated.connect(self.update_image_label)
        self.offset = 23

        # Create and start the screenshot thread
        self.screenshot_thread = threading.Thread(target=self.update_screenshot_thread)
        self.screenshot_thread.start()

        self.setWindowTitle(str(self.window))
        self.setMinimumSize(960 + self.offset, 540 + self.offset)
        self.next_monitor_button.clicked.connect(self.handle_next_monitor_click)
        self.previous_monitor_button.clicked.connect(self.handle_previous_monitor_click)


    def handle_next_monitor_click(self):
        if self.monitor < self.client_monitors:
            self.monitor += 1
            self.my_window.bluepill.send(b"monitor->" + str(self.monitor).encode('utf-8'), self.my_window.connection[self.window])
            
    def handle_previous_monitor_click(self):
        if self.monitor > 0:
            self.monitor -= 1
            self.my_window.bluepill.send(b"monitor->" + str(self.monitor).encode('utf-8'), self.my_window.connection[self.window])
            
        
    def handle_button_click(self):
        # Get the selected number from the spinner and print it
        selected_number = self.number_spinner.value()
        self.my_window.bluepill.send(b"quality->" + str(selected_number).encode('utf-8'), self.my_window.connection[self.window])

    def closeEvent(self, event):
        self.my_window.bluepill.send(b"stream", self.my_window.connection[self.window])
        self.active_stream = False
        self.screenshot_thread.join()  # Wait for the screenshot thread to finish
        event.accept()
        self.my_window.remote_window[self.window] = False

    def update_screenshot_thread(self):
        last_stream = None  # Store the last observed stream
        with mss.mss() as sct:
            while self.active_stream:
                current_stream = self.my_window.stream[self.window]
                if current_stream != last_stream:
                    pixmap = self.resize_image(current_stream)
                    self.imageUpdateSignal.imageUpdated.emit(pixmap)
                    last_stream = current_stream
                    continue
                time.sleep(0.03)
                
    def resize_image(self, image_bytes):
        image = QImage.fromData(image_bytes)
        size = self.image_label.size()
        image = image.scaled(size, Qt.IgnoreAspectRatio)
        pixmap = QPixmap.fromImage(image)
        return pixmap

    def update_image_label(self, pixmap):
        self.image_label.setPixmap(pixmap)

    def button_clicked(self):
        print("Button Clicked")
