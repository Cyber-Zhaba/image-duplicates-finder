import hashlib
import cv2
import numpy as np

from string import hexdigits
import imagehash
from PIL import Image


def sha256_hash(img_path):
    with open(img_path, "rb") as f:
        file_hash = hashlib.sha256()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def perceptual_hash(img_path):
    image = Image.open(img_path)
    return imagehash.phash(image)


def apply_convolution(img, kernel, stride=1):
    result = cv2.filter2D(img, -1, kernel)
    if stride > 1:
        result = result[::stride, ::stride]
    return result


def compress512to8(img):
    kernel_size = 65
    stride = 56
    # Why 65 and 56? Well, they look cool, idk...
    kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size**2)

    return apply_convolution(img, kernel, stride)


def hexmask(img8x8, rgb=True):
    def quantize(pixel):
        # ITU-R BT.601 conversion to grayscale
        if rgb:
            gray = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
        else:
            gray = pixel
        return round(gray * 15 / 255)

    brightness_mask = ""

    for x in range(8):
        for y in range(8):
            brightness_idx = quantize(img8x8[x, y])
            brightness_mask += hexdigits[brightness_idx]

    return brightness_mask


def convolution_hash(img_path):
    img_bgr = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img8x8 = compress512to8(img_rgb)
    return hexmask(img8x8)


def sobel_hash(img_path):
    img_bgr = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    kernel = np.array([
        [+1, 0, -1],
        [+2, 0, -2],
        [+1, 0, -1]
    ])

    img_sobel = apply_convolution(img_rgb, kernel, stride=1)
    img8x8 = compress512to8(img_sobel)
    return hexmask(img8x8)


def sharpen_hash(img_path):
    img_bgr = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])

    img_sharpened = apply_convolution(img_rgb, kernel, stride=1)
    img8x8 = compress512to8(img_sharpened)
    return hexmask(img8x8)

def gray_convolution_hash(img_path):
    img_bgr = cv2.imread(img_path)
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    img8x8 = compress512to8(img_gray)
    return hexmask(img8x8, False)
