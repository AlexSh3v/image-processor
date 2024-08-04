import io
from PIL import Image
from django.core.files.base import ContentFile


def crop(original_image, crop_x, crop_y, crop_width, crop_height):
    # Открываем оригинальное изображение
    image = Image.open(original_image)
    
    crop_x = int(crop_x)
    crop_y = int(crop_y)
    crop_width = int(crop_width)
    crop_height = int(crop_height)

    cropped_image = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))

    buffer = io.BytesIO()
    # TODO: get FORMAT png/jpeg/gif data also!
    cropped_image.save(buffer, format='JPEG')
    buffer.seek(0)

    return ContentFile(buffer.read(), name='processed_image.jpg')
