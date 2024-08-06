import enum
import io
import pathlib
from typing import Literal, Union
from PIL import Image, ExifTags, ImageFilter, ImageOps
from PIL.ImageFile import ImageFile
import numpy as np
from django.core.files.base import ContentFile


available_types = [
    'none', 
    'sepia', 
    'grayscale', 
    'invert', 
    'blur',
]
FilterType = Literal[*available_types]

def apply_sepia(img: Image):
    img = img.convert('RGBA')
    data = np.array(img)
    sepia_data = np.zeros(data.shape, dtype=np.uint8)
    tr = (0.393 * data[:, :, 0] + 0.769 * data[:, :, 1] + 0.189 * data[:, :, 2]).clip(0, 255)
    tg = (0.349 * data[:, :, 0] + 0.686 * data[:, :, 1] + 0.168 * data[:, :, 2]).clip(0, 255)
    tb = (0.272 * data[:, :, 0] + 0.534 * data[:, :, 1] + 0.131 * data[:, :, 2]).clip(0, 255)
    sepia_data[:, :, 0] = tr
    sepia_data[:, :, 1] = tg
    sepia_data[:, :, 2] = tb
    sepia_data[:, :, 3] = data[:, :, 3]
    sepia_img = Image.fromarray(sepia_data, 'RGBA')
    return sepia_img


def crop(original_image: ImageFile, 
         crop_x: int, 
         crop_y: int, 
         crop_width: int, 
         crop_height: int) -> ContentFile:
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
    image = original_image

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
    return cropped_image


def filter_(img: ImageFile, filter_type: FilterType) -> ImageFile:
    if filter_type == 'none':
        pass
    elif filter_type == 'grayscale':
        img = img.convert('L')
    elif filter_type == 'sepia':
        img = apply_sepia(img)
    elif filter_type == 'blur':
        img = img.filter(ImageFilter.BLUR)
    elif filter_type == 'invert':
        if img.mode not in ('L', 'RGB'):
            img = img.convert('RGB')
        img = ImageOps.invert(img)
    else:
        raise ValueError(f"Unknown filter type. Use one of these: {FilterType}.")

    ###########################
    if DEBUG:
        img.show()
    ###########################

    return img


def get_image(by_path: pathlib.Path) -> ImageFile:
    return Image.open(by_path)

def convert_to_content_file(image_object: ImageFile, suffix: str) -> ContentFile:
    if suffix.lower() == '.jpg':
        suffix = '.jpeg'
        if image_object.mode.lower() in ('rgb', 'rgba'):
            suffix = '.png'
    file_format = suffix.strip('.')
    print(f'[Img2ContentFile] suffix: {suffix}')
    print(f'[Img2ContentFile] file format: {file_format}')
    buffer = io.BytesIO()
    image_object.save(buffer, format=file_format)
    buffer.seek(0)
    unimportant_filename = f'new_image{suffix}'
    print(f'[Img2ContentFile] new (unimportant) filename: {unimportant_filename}')
    return ContentFile(buffer.read(), name=unimportant_filename)


DEBUG = False
if __name__ == '__main__':
    DEBUG = True
    filters = [
        'none',
        'grayscale',
        # 'sepia',
        # 'invert',
        # 'blur',
    ]
    print(FilterType)
    p = pathlib.Path(r'C:\Users\Alex & Vadimka\Documents\projects\image-processor\media\uploads\processed_image.png')
    print(p.name)
    for f in filters:
        print(f, filter_(p, f))
