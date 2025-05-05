import cv2
import numpy as np
import os

class ImageProcessor:
    def __init__(self):
        pass
    
    def load_image(self, file_path):
        try:
            if not os.path.exists(file_path):
                print(f"Error: File does not exist at {file_path}")
                return None
                
            image = cv2.imread(file_path)
            if image is None:
                print(f"Error: Could not load image at {file_path}")
                return None
            return image
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            return None
    
    def save_image(self, image, file_path):
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            result = cv2.imwrite(file_path, image)
            if not result:
                print(f"Error: OpenCV could not save image to {file_path}")
                return False
                
            print(f"Image saved successfully to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return False
    
    def rotate_image(self, image, angle):
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        abs_cos = abs(rotation_matrix[0, 0])
        abs_sin = abs(rotation_matrix[0, 1])
        
        new_width = int(height * abs_sin + width * abs_cos)
        new_height = int(height * abs_cos + width * abs_sin)
        
        rotation_matrix[0, 2] += new_width / 2 - center[0]
        rotation_matrix[1, 2] += new_height / 2 - center[1]
        
        rotated_image = cv2.warpAffine(image, rotation_matrix, (new_width, new_height), 
                                       flags=cv2.INTER_LINEAR, 
                                       borderMode=cv2.BORDER_CONSTANT, 
                                       borderValue=(255, 255, 255))
        return rotated_image
    
    def resize_image(self, image, scale_factor):
        if scale_factor <= 0:
            return image
            
        height, width = image.shape[:2]
        new_height = int(height * scale_factor)
        new_width = int(width * scale_factor)
        
        if new_width <= 0 or new_height <= 0:
            return image
            
        resized_image = cv2.resize(image, (new_width, new_height), 
                                  interpolation=cv2.INTER_AREA if scale_factor < 1 else cv2.INTER_LINEAR)
        return resized_image
    
    def bgr_to_rgb(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)