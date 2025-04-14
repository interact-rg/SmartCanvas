from time import perf_counter
import cv2
import numpy as np
from smart_canvas.filters.base import Filter
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from cv2.typing import MatLike


class SketchModel(Filter):

    background = 'sketch.jpg'

    def __init__(self):
        super().__init__()
        
        self.model_path = "models/face_stylizer_color_sketch.task"

        BaseOptions = mp.tasks.BaseOptions
        Facestylizer = mp.tasks.vision.FaceStylizer
        FacestylizerOptions = mp.tasks.vision.FaceStylizerOptions
        options = FacestylizerOptions(
            base_options=BaseOptions(model_asset_path="models/face_stylizer_color_sketch.task"))
        self.stylizer = Facestylizer.create_from_options(options) 

    def filter(self, frame: MatLike):
        original_height, original_width = frame.shape[:2]
        original_dims = (original_width, original_height)

        try:    
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        except Exception as e:
            print(f"Error during frame resizing or color conversion for model: {e}")
            return frame

        # Create a fresh stylizer instance each time
        try:
            BaseOptions = mp.tasks.BaseOptions
            Facestylizer = mp.tasks.vision.FaceStylizer
            FacestylizerOptions = mp.tasks.vision.FaceStylizerOptions
            
            options = FacestylizerOptions(
                base_options=BaseOptions(model_asset_path=self.model_path))
            
            # Create a new stylizer for each call
            with Facestylizer.create_from_options(options) as stylizer:
                face_stylizer_result = stylizer.stylize(mp_image)
                if face_stylizer_result is not None:
                    # Convert to numpy array
                    styled_image = face_stylizer_result.numpy_view()
                    
                    # Convert back to BGR for OpenCV
                    styled_image_bgr = cv2.cvtColor(styled_image, cv2.COLOR_RGB2BGR)
                    
                    # Resize to original dimensions
                    resized_image = cv2.resize(styled_image_bgr, original_dims, 
                                               interpolation=cv2.INTER_LINEAR)
                    
                    return resized_image
                else:
                    print("Face stylizer returned None")
                    return frame
        except Exception as e:
            print(f"Error in face stylization: {e}")
            return frame

        # Fallback return in case of any other issues
        return frame

    def filter_frame(self, frame: MatLike, mask: MatLike) -> MatLike:
        """Override to bypass background masking for artistic filters."""
        startTime = perf_counter()
        
        # Just apply the filter - no background masking
        result = self.filter(frame)
        
        # Keep timing calculations from parent method
        endTime = perf_counter()
        self.timing_samples.append(endTime - startTime)
        if len(self.timing_samples) > 0:
            self.average_time = float(np.mean(self.timing_samples))
        
        return result
