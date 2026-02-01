import sys
import os
import requests

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QFileDialog,
    QLineEdit,
    QMessageBox,
)

class SenderWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Media Sender")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        # Receiver address input
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Receiver IP (e.g. 192.168.1.50:5000)")
        layout.addWidget(self.address_input)

        # Token input
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Security token")
        layout.addWidget(self.token_input)

        # Selected file label
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        # Select file button
        self.select_button = QPushButton("Select File")
        self.select_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_button)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_file)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

        self.selected_file = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            os.getcwd(),
            "All Files (*)"
        )

        if file_path:
            self.selected_file = file_path
            self.file_label.setText(os.path.basename(file_path))

    def send_file(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Error", "No file selected")
            return

        address = self.address_input.text().strip()
        token = self.token_input.text().strip()

        if not address:
            QMessageBox.warning(self, "Error", "Enter receiver IP and port")
            return
        
        if not token:
            QMessageBox.warning(self, "Error", "Enter security token")
            return
        
        url = f"http://{address}/upload_gif"

        try:
            with open(self.selected_file, "rb") as f:
                files = {"gif": f}
                headers = {"Authorization": token}
                response = requests.post(url, files=files, headers=headers, timeout=10)

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "File sent successfully")
            else:
                QMessageBox.warning(self, "Error", f"Server error: {response.status_code}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SenderWindow()
    window.show()
    sys.exit(app.exec())