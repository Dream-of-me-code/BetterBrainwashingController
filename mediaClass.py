import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QSlider
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from Network_server import start_network_server

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

    open_gif_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.open_gif_signal.connect(self.open_gif_from_network)

        self.setWindowTitle("Control Panel")
        self.setGeometry(100, 100, 200, 100)
        self.current_directory = os.path.dirname(__file__)
        layout = QVBoxLayout()

        #Select File Button
        self.select_file_button = QPushButton("Select Gif file")
        self.select_file_button.clicked.connect(self.select_gif_file)
        layout.addWidget(self.select_file_button)

        #Open GIF Button
        self.open_gif_button = QPushButton("Open GIF")
        self.open_gif_button.clicked.connect(self.open_gif)
        layout.addWidget(self.open_gif_button)

        #Select Folder Button
        self.select_dir_button = QPushButton("Select Gif Folder")
        self.select_dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_button)
        
        #Open All GIFs in Directory Button
        self.open_all_gifs_in_directory_button  = QPushButton("Open All GIFs in Folder")
        self.open_all_gifs_in_directory_button.clicked.connect(self.open_all_gifs_in_directory)
        layout.addWidget(self.open_all_gifs_in_directory_button)

        #Delay Slider
        self.delay_label = QLabel("Delay: 500 ms")
        layout.addWidget(self.delay_label)
        self.delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_slider.setMinimum(0)
        self.delay_slider.setMaximum(3000)
        self.delay_slider.setValue(500)
        self.delay_slider.valueChanged.connect(self.update_delay_label)
        layout.addWidget(self.delay_slider)


        self.spawn_delay_ms = 500
        self._gif_queue = []
        self._spawn_timer = QTimer(self)
        self._spawn_timer.timeout.connect(self.spawn_next_gif)


        self.setLayout(layout)
        self.gif_windows = []

        self.current_gif_path = os.path.join(os.path.dirname(__file__), "0.gif")

        self.show()

    def open_gif_from_network(self, gif_path):

        window = GifWindow(gif_path, os.path.basename(gif_path))
        self.gif_windows.append(window)

    def open_gif(self):
        window = GifWindow(self.current_gif_path, os.path.basename(self.current_gif_path))
        self.gif_windows.append(window)

    def open_all_gifs_in_directory(self):
        if not os.path.isdir(self.current_directory):
            return
        
        self._gif_queue = [
            os.path.join(self.current_directory, f)
            for f in os.listdir(self.current_directory)
            if f.lower().endswith(".gif")
        ]

        if not self._gif_queue:
            return
        
        self._spawn_timer.start(self.spawn_delay_ms)

    def spawn_next_gif(self):
        if not self._gif_queue:
            self._spawn_timer.stop()
            return
        
        gif_path = self._gif_queue.pop(0)
        window = GifWindow(gif_path, os.path.basename(gif_path))
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

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select GIF Folder",
            self.current_directory
        )

        if directory:
            self.current_directory = directory
            self.select_dir_button.setText(
                f"Folder: {os.path.basename(directory)}"
            )

    def update_delay_label(self, value):
        self.spawn_delay_ms = value
        self.delay_label.setText(f"Delay: {value} ms")

        if self._spawn_timer.isActive():
            self._spawn_timer.setInterval(value)

    def closeEvent(self, event):
        for window in self.gif_windows:
            window.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    control_win = ControlWindow()

    start_network_server(control_win)
    sys.exit(app.exec())