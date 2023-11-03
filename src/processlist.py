import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt5.QtCore import Qt

class ProcessList(QMainWindow):
    def __init__(self, window_name):
        super().__init__()
        self.window_name = window_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle("ProcessList {}".format(self.window_name))
        self.setGeometry(100, 100, 600, 400)  # Set the initial window size

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QTableWidget with 4 columns
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "PID", "CPU USAGE", "MEMORY USAGE"])

        # Set an initial width for each column
        self.tableWidget.setColumnWidth(0, 150)  # Name
        self.tableWidget.setColumnWidth(1, 100)  # PID
        self.tableWidget.setColumnWidth(2, 150)  # CPU USAGE
        self.tableWidget.setColumnWidth(3, 150)  # MEMORY USAGE

        # Enable interactive resizing for columns
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)

        # Allow the user to resize rows
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Set selection behavior to select entire rows
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)

        # Set selection mode and options for rows
        self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setFocusPolicy(Qt.NoFocus)  # Remove the focus border

        # Set dark mode style
        dark_style = """
        QTableWidget {
            background-color: #222;
            color: #fff;
            gridline-color: #444;
        }
        QTableWidget::item:selected {
            background-color: #007ACC;
            color: #fff;
        }
        QHeaderView::section {
            background-color: #222;
            color: #fff;
        }
        """
        self.tableWidget.setStyleSheet(dark_style)

        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tableWidget)

    def addpid(self, value):
        self.tableWidget.setRowCount(0)  # Clear all existing rows

        for item in value:
            process_name = item['ProcessName']
            process_id = str(item['ProcessId'])
            cpu_usage = str(item['CpuUsage'])
            memory_usage = str(item['MemoryUsageKB'])

            rowPosition = self.tableWidget.rowCount()
            self.tableWidget.insertRow(rowPosition)

            name_item = QTableWidgetItem(process_name)
            pid_item = QTableWidgetItem(process_id)
            cpu_usage_item = QTableWidgetItem(cpu_usage)
            memory_usage_item = QTableWidgetItem(memory_usage)

            self.tableWidget.setItem(rowPosition, 0, name_item)
            self.tableWidget.setItem(rowPosition, 1, pid_item)
            self.tableWidget.setItem(rowPosition, 2, cpu_usage_item)
            self.tableWidget.setItem(rowPosition, 3, memory_usage_item)
