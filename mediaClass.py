import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt

class GifWindow(QWidget):
    def __init__(self, gif_path, title="Gif Player" ):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not os.path.isabs(gif_path):
            gif_path = os.path.join(os.path.dirname(__file__), gif_path)


        self.movie = QMovie(gif_path)
        self.label.setMovie(self.movie)
        self.movie.start()

        size = self.movie.frameRect().size()
        self.label.setFixedSize(size)
        self.resize(size)
        self.show()

        self._drag_active = False
        self._drag_start_pos = None
        self._window_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._drag_active = True
            self._drag_start_pos = event.globalPosition()
            self._window_start_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            delta = event.globalPosition() - self._drag_start_pos
            delta_point = delta.toPoint()
            new_pos = self._window_start_pos + delta_point
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._drag_active = False
        elif event.button() == Qt.MouseButton.LeftButton:
            self.close()
        event.accept()
            
class ControlWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Control Panel")
        self.setGeometry(100, 100, 200, 100)

        layout = QVBoxLayout()

        #Open GIF Button
        self.open_gif_button = QPushButton("Open GIF")
        self.open_gif_button.clicked.connect(self.open_gif)
        layout.addWidget(self.open_gif_button)

        #Select File Button
        self.select_file_button = QPushButton("Select Gif file")
        self.select_file_button.clicked.connect(self.select_gif_file)
        layout.addWidget(self.select_file_button)

        self.setLayout(layout)
        self.gif_windows = []

        self.current_gif_path = os.path.join(os.path.dirname(__file__), "0.gif")

        self.show()

    def open_gif(self):
        window = GifWindow(self.current_gif_path, os.path.basename(self.current_gif_path))
        self.gif_windows.append(window)

    def select_gif_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select GIF",
            os.path.dirname(__file__),
            "GIF Files (*.gif)"
        )
        if file_path:
            self.current_gif_path = file_path

            window = GifWindow(self.current_gif_path, os.path.basename(self.current_gif_path))
            self.gif_windows.append(window)

    def closeEvent(self, event):
        for window in self.gif_windows:
            window.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    control_win = ControlWindow()

    sys.exit(app.exec())