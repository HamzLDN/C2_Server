
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget

def side_menus(window):
    # Create a sidebar layout
    sidebar_layout = QVBoxLayout()
    sidebar_widget = QWidget(window)
    sidebar_widget.setLayout(sidebar_layout)

    # Create a central widget
    central_widget = QWidget(window)

    # Set up the main layout for the central widget
    main_layout = QVBoxLayout(central_widget)

    # Create sidebar buttons for menus
    menu1_button = QPushButton("Menu 1")
    menu2_button = QPushButton("Menu 2")
    menu3_button = QPushButton("Menu 3")
    menu4_button = QPushButton("Menu 4")

    # Connect button signals to functions to change window content
    menu1_button.clicked.connect(show_menu1)
    menu2_button.clicked.connect(show_menu2)
    menu3_button.clicked.connect(show_menu3)
    menu4_button.clicked.connect(show_menu4)

    # Add buttons to the sidebar layout
    sidebar_layout.addWidget(menu1_button)
    sidebar_layout.addWidget(menu2_button)
    sidebar_layout.addWidget(menu3_button)
    sidebar_layout.addWidget(menu4_button)

    # Set the sidebar as the menu widget
    window.setMenuWidget(sidebar_widget)

    # Set the central widget
    window.setCentralWidget(central_widget)
def show_menu1(self):
    # Replace with your logic for Menu 1
    self.setWindowTitle("Menu 1")
    # Clear the central widget or add Menu 1 content

def show_menu2(self):
    # Replace with your logic for Menu 2
    self.setWindowTitle("Menu 2")
    # Clear the central widget or add Menu 2 content

def show_menu3(self):
    # Replace with your logic for Menu 3
    self.setWindowTitle("Menu 3")
    # Clear the central widget or add Menu 3 content

def show_menu4(self):
    # Replace with your logic for Menu 4
    self.setWindowTitle("Menu 4")
    # Clear the central widget or add Menu 4 content
