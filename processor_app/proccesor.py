import io
import pathlib
from PIL import Image, ExifTags
from django.core.files.base import ContentFile


def crop(original_image: pathlib.Path, 
         crop_x: int, 
         crop_y: int, 
         crop_width: int, 
         crop_height: int):
    """Crop image into memory. Return as ContentFile from django.

    Args:
        original_image (pathlib.Path): path to image in filesystem
        crop_x (int): left top x coord of cropped image
        crop_y (int): right top y coord of cropped image
        crop_width (int): width of cropped image
        crop_height (int): height of cropped image

    Returns:
        ContentFile: django image
    """
    image = Image.open(original_image)

    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        print('Error!')
        pass

    crop_x = int(crop_x)
    crop_y = int(crop_y)
    crop_width = int(crop_width)
    crop_height = int(crop_height)

    cropped_image = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))

    buffer = io.BytesIO()
    # TODO: get FORMAT png/jpeg/gif data also!
    cropped_image.save(buffer, format='png')
    buffer.seek(0)

    return ContentFile(buffer.read(), name='processed_image.png')
