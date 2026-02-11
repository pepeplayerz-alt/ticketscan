import os
import uuid


STATIC_DIR = "static"
IMAGES_DIR = "receipt_images"
FULL_IMAGES_PATH = os.path.join(STATIC_DIR, IMAGES_DIR)

def save_uploaded_image(image_bytes, original_filename="image.jpg"):
    """
    Save bytes to a file with a UUID name.
    Returns the path relative to the static directory (e.g. 'receipt_images/uuid.jpg').
    """
    try:
        ext = original_filename.split('.')[-1]
    except:
        ext = "jpg"
    
    filename = f"{uuid.uuid4()}.{ext}"
    os.makedirs(FULL_IMAGES_PATH, exist_ok=True)
    
    file_path = os.path.join(FULL_IMAGES_PATH, filename)
    
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    return f"{IMAGES_DIR}/{filename}"

def delete_image(image_path_relative):
    """
    Delete the image file given its relative path (e.g. 'receipt_images/uuid.jpg').
    Returns True if deleted or didn't exist, False if error.
    """
    if not image_path_relative:
        return True
        
    try:
        
        full_path = os.path.join(STATIC_DIR, image_path_relative)
        
        if os.path.exists(full_path):
            os.remove(full_path)
        return True
    except Exception:
        return False
