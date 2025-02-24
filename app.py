import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QCheckBox, QFileDialog, QHBoxLayout, QVBoxLayout,
    QStatusBar, QMessageBox, QFrame
)
from PyQt6.QtGui import QPixmap, QImage, QPalette, QLinearGradient, QColor
from PyQt6.QtCore import Qt, QPoint,QPointF
from PIL import Image, ImageQt
import io

class GradientWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setAutoFillBackground(True)
        gradient = QLinearGradient(QPointF(0, 0), QPointF(self.width(), self.height()))
        gradient.setColorAt(0, QColor("#FFA500"))  # Orange
        gradient.setColorAt(1, QColor("#FFD700"))  # Yellow
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(palette)

class ImageResizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Resizer BY HASEEB RAZA")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize variables
        self.original_image = None
        self.resized_image = None
        self.original_aspect_ratio = 1.0
        
        # Create gradient background widget
        gradient_widget = GradientWidget()
        self.setCentralWidget(gradient_widget)
        
        # Create main container
        self.main_container = QWidget()
        
        # Image display labels with styling
        self.original_image_label = QLabel("Original Image")
        self.original_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_image_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 10px;
                padding: 10px;
                min-width: 300px;
                min-height: 300px;
            }
        """)
        
        self.resized_image_label = QLabel("Resized Image")
        self.resized_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resized_image_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 10px;
                padding: 10px;
                min-width: 300px;
                min-height: 300px;
            }
        """)
        
        # Buttons with styling
        button_style = """
            QPushButton {
                background-color: #FF8C00;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """
        
        self.open_button = QPushButton("Open Image")
        self.open_button.setStyleSheet(button_style)
        
        self.save_button = QPushButton("Save Image")
        self.save_button.setStyleSheet(button_style)
        self.save_button.setEnabled(False)
        
        # Input fields with styling
        input_style = """
            QLineEdit {
                padding: 5px;
                border: 2px solid #FFA500;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 200);
            }
        """
        
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width")
        self.width_input.setStyleSheet(input_style)
        
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height")
        self.height_input.setStyleSheet(input_style)
        
        # Checkbox with styling
        self.aspect_ratio_check = QCheckBox("Maintain Aspect Ratio")
        self.aspect_ratio_check.setStyleSheet("""
            QCheckBox {
                color: #444444;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 150);
                padding: 5px;
                border-radius: 5px;
            }
        """)
        self.aspect_ratio_check.setChecked(True)
        
        # Create layouts
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.width_input)
        input_layout.addWidget(self.height_input)
        input_layout.addWidget(self.aspect_ratio_check)
        input_layout.setSpacing(10)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.save_button)
        button_layout.setSpacing(10)
        
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.original_image_label)
        image_layout.addWidget(self.resized_image_label)
        image_layout.setSpacing(20)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(image_layout)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.main_container.setLayout(main_layout)
        gradient_widget.setLayout(QVBoxLayout())
        gradient_widget.layout().addWidget(self.main_container)
        
        # Status bar with styling
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(255, 255, 255, 180);
                color: #444444;
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        
        # Connect signals
        self.open_button.clicked.connect(self.open_image)
        self.save_button.clicked.connect(self.save_image)
        self.width_input.textEdited.connect(lambda: self.resize_image(True))
        self.height_input.textEdited.connect(lambda: self.resize_image(False))
        self.aspect_ratio_check.stateChanged.connect(self.toggle_aspect_ratio)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.resized_image = None
                self.original_aspect_ratio = self.original_image.width / self.original_image.height
                
                self.width_input.setText(str(self.original_image.width))
                self.height_input.setText(str(self.original_image.height))
                
                self.display_image(self.original_image, self.original_image_label)
                self.save_button.setEnabled(False)
                self.status_bar.showMessage("Image loaded successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def resize_image(self, width_changed):
        if not self.original_image:
            return
            
        try:
            width_text = self.width_input.text()
            height_text = self.height_input.text()
            
            if not width_text or not height_text:
                return
                
            new_width = int(width_text)
            new_height = int(height_text)
            
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Dimensions must be positive numbers")
                
            if self.aspect_ratio_check.isChecked():
                if width_changed:
                    new_height = int(new_width / self.original_aspect_ratio)
                    self.height_input.blockSignals(True)
                    self.height_input.setText(str(new_height))
                    self.height_input.blockSignals(False)
                else:
                    new_width = int(new_height * self.original_aspect_ratio)
                    self.width_input.blockSignals(True)
                    self.width_input.setText(str(new_width))
                    self.width_input.blockSignals(False)
            
            self.resized_image = self.original_image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            
            self.display_image(self.resized_image, self.resized_image_label)
            self.save_button.setEnabled(True)
            self.status_bar.showMessage("Image resized successfully")
            
        except ValueError as e:
            self.status_bar.showMessage(f"Error: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Resizing failed: {str(e)}")

    def display_image(self, image, label):
        try:
            qt_image = ImageQt.ImageQt(image)
            pixmap = QPixmap.fromImage(qt_image)
            
            scaled_pixmap = pixmap.scaled(
                label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to display image: {str(e)}")

    def save_image(self):
        if not self.resized_image:
            return
            
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Image", "", 
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;BMP Image (*.bmp)"
        )
        
        if file_path:
            try:
                # Add appropriate extension if missing
                if not any(file_path.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.bmp')):
                    if "PNG" in selected_filter:
                        file_path += '.png'
                    elif "JPEG" in selected_filter:
                        file_path += '.jpg'
                    elif "BMP" in selected_filter:
                        file_path += '.bmp'

                # Convert to RGB if saving as JPEG
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    if self.resized_image.mode in ('RGBA', 'P'):
                        self.resized_image = self.resized_image.convert('RGB')

                self.resized_image.save(file_path)
                self.status_bar.showMessage(f"Image saved successfully to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")

    def toggle_aspect_ratio(self):
        if self.aspect_ratio_check.isChecked() and self.original_image:
            self.original_aspect_ratio = self.original_image.width / self.original_image.height
            self.resize_image(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.original_image:
            self.display_image(self.original_image, self.original_image_label)
        if self.resized_image:
            self.display_image(self.resized_image, self.resized_image_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageResizerApp()
    window.show()
    sys.exit(app.exec())