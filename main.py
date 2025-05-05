import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                            QSlider, QScrollArea)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
import cv2
from image import ImageProcessor

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QApplication.applicationDirPath()

class ImageEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Image Editor")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(800, 600)
        
        self.image_processor = ImageProcessor()
        self.current_image = None
        self.original_image = None
        self.scale_factor = 1.0
        self.original_size = (0, 0)
        
        self.init_ui()
        
    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.upload_widget = QWidget()
        self.upload_layout = QVBoxLayout(self.upload_widget)
        
        self.upload_button = QPushButton("Upload Image")
        self.upload_button.setFixedSize(200, 50)
        self.upload_button.clicked.connect(self.upload_image)
        self.upload_layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)
        
        self.edit_widget = QWidget()
        self.edit_layout = QVBoxLayout(self.edit_widget)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumSize(780, 450)
        self.scroll_area.setMaximumSize(780, 450)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        
        self.edit_layout.addWidget(self.scroll_area)
        
        self.info_label = QLabel("No image loaded")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.edit_layout.addWidget(self.info_label)
        
        self.controls_layout = QHBoxLayout()
        
        self.rotate_left_button = QPushButton("Rotate Left")
        self.rotate_left_button.clicked.connect(self.rotate_left)
        self.controls_layout.addWidget(self.rotate_left_button)
        
        self.rotate_right_button = QPushButton("Rotate Right")
        self.rotate_right_button.clicked.connect(self.rotate_right)
        self.controls_layout.addWidget(self.rotate_right_button)
        
        self.scale_slider_layout = QVBoxLayout()
        self.scale_label = QLabel("Scale: 100%")
        self.scale_slider_layout.addWidget(self.scale_label, alignment=Qt.AlignCenter)
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(200)
        self.scale_slider.setValue(100)
        self.scale_slider.setTickInterval(10)
        self.scale_slider.setTickPosition(QSlider.TicksBelow)
        self.scale_slider.valueChanged.connect(self.scale_image)
        self.scale_slider_layout.addWidget(self.scale_slider)
        
        self.controls_layout.addLayout(self.scale_slider_layout)
        
        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)
        self.controls_layout.addWidget(self.save_button)
        
        self.go_back_button = QPushButton("Go Back")
        self.go_back_button.clicked.connect(self.go_back)
        self.controls_layout.addWidget(self.go_back_button)
        
        self.edit_layout.addLayout(self.controls_layout)
        
        self.main_layout.addWidget(self.upload_widget)
        self.main_layout.addWidget(self.edit_widget)
        
        self.edit_widget.hide()
        
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            self.original_image = self.image_processor.load_image(file_path)
            if self.original_image is not None:
                self.current_image = self.original_image.copy()
                self.original_size = (self.original_image.shape[1], self.original_image.shape[0])  # width, height
                self.update_image_display()
                self.upload_widget.hide()
                self.edit_widget.show()
    
    def update_image_display(self):
        if self.current_image is not None:
            display_image = self.current_image.copy()
            
            current_height, current_width = display_image.shape[:2]
            current_size = (current_width, current_height)
            
            scaled_width = int(current_width * self.scale_factor)
            scaled_height = int(current_height * self.scale_factor)
            scaled_size = (scaled_width, scaled_height)
            
            if self.scale_factor != 1.0:
                display_image = self.image_processor.resize_image(display_image, self.scale_factor)
            
            max_width = self.scroll_area.width() - 20
            max_height = self.scroll_area.height() - 20
            
            display_width = scaled_width
            display_height = scaled_height
            
            if display_width > max_width or display_height > max_height:
                width_ratio = max_width / display_width
                height_ratio = max_height / display_height
                ratio = min(width_ratio, height_ratio)
                
                display_width = int(display_width * ratio)
                display_height = int(display_height * ratio)
            
            rgb_image = self.image_processor.bgr_to_rgb(display_image)
            
            height, width = display_image.shape[:2]
            bytes_per_line = 3 * width
            
            q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            if width != display_width or height != display_height:
                pixmap = pixmap.scaled(display_width, display_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.image_label.setPixmap(pixmap)
            self.image_label.setFixedSize(pixmap.size())
            
            original_text = f"Original: {self.original_size[0]}x{self.original_size[1]}"
            current_text = f"Current: {current_size[0]}x{current_size[1]}"
            scaled_text = f"Scaled: {scaled_size[0]}x{scaled_size[1]}"
            display_text = f"Display: {display_width}x{display_height}"
            
            self.info_label.setText(f"{original_text} | {current_text} | {scaled_text} | {display_text}")
            
    def rotate_left(self):
        if self.current_image is not None:
            self.current_image = self.image_processor.rotate_image(self.current_image, 90)
            self.update_image_display()
    
    def rotate_right(self):
        if self.current_image is not None:
            self.current_image = self.image_processor.rotate_image(self.current_image, -90)
            self.update_image_display()
    
    def scale_image(self, value):
        self.scale_factor = value / 100.0
        self.scale_label.setText(f"Scale: {value}%")
        self.update_image_display()
    
    def save_image(self):
        if self.current_image is not None:
            save_image = self.current_image
            if self.scale_factor != 1.0:
                save_image = self.image_processor.resize_image(save_image, self.scale_factor)
                
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, 
                "Save Image", 
                "", 
                "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)"
            )
            
            if file_path:
                if "PNG" in selected_filter and not file_path.lower().endswith('.png'):
                    file_path += '.png'
                elif "JPEG" in selected_filter and not (file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg')):
                    file_path += '.jpg'
                elif "BMP" in selected_filter and not file_path.lower().endswith('.bmp'):
                    file_path += '.bmp'
                    
                self.image_processor.save_image(save_image, file_path)
    
    def go_back(self):
        self.edit_widget.hide()
        self.upload_widget.show()
        self.current_image = None
        self.original_image = None
        self.scale_factor = 1.0
        self.scale_slider.setValue(100)
        self.scale_label.setText("Scale: 100%")
        self.image_label.clear()
        self.info_label.setText("No image loaded")

def exception_hook(exctype, value, traceback):
    print(f"Exception: {exctype}, {value}")
    sys.__excepthook__(exctype, value, traceback)
    sys.exit(1)

if __name__ == "__main__":
    sys.excepthook = exception_hook

    
    app = QApplication(sys.argv)
    window = ImageEditorApp()
    window.show()
    sys.exit(app.exec_())