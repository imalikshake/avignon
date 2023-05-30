import functools
import os
from matplotlib import gridspec
import matplotlib.pylab as plt
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import PIL


def crop_center(image):
    """
    Crop the input image to a square shape.

    Parameters:
    - image: Input image.

    Returns:
    - Cropped square image.
    """
    shape = image.shape
    new_shape = min(shape[1], shape[2])
    offset_y = max(shape[1] - shape[2], 0) // 2
    offset_x = max(shape[2] - shape[1], 0) // 2
    image = tf.image.crop_to_bounding_box(image, offset_y, offset_x, new_shape, new_shape)
    return image

@functools.lru_cache(maxsize=None)
def load_image(image_url, image_size=(256, 256), crop=False, preserve_aspect_ratio=True):
    """
    Loads and preprocesses images from the given URL.

    Parameters:
    - image_url: URL of the image.
    - image_size: Desired size of the image. Default is (256, 256).
    - crop: Whether to crop the image to a square shape. Default is False.
    - preserve_aspect_ratio: Whether to preserve the aspect ratio of the image during resizing. Default is True.

    Returns:
    - Preprocessed image tensor.
    """
    # Cache image file locally.
    image_path = image_url
    # Load and convert to float32 numpy array, add batch dimension, and normalize to range [0, 1].
    img = tf.io.decode_image(tf.io.read_file(image_path), channels=3, dtype=tf.float32)[tf.newaxis, ...]

    if image_size != 0:
        img = tf.image.resize(img, image_size, preserve_aspect_ratio=True)
    if crop:
        img = crop_center(img)
    return img

def show_n(images, titles=('',)):
    """
    Display multiple images in a grid.

    Parameters:
    - images: List of images to display.
    - titles: List of titles for the images. Default is ('',).

    Returns:
    - None
    """
    n = len(images)
    image_sizes = [image.shape[1] for image in images]
    w = (image_sizes[0] * 6) // 320
    plt.figure(figsize=(w * n, w))
    gs = gridspec.GridSpec(1, n, width_ratios=image_sizes)
    for i in range(n):
        plt.subplot(gs[i])
        plt.imshow(images[i][0], aspect='equal')
        plt.axis('off')
        plt.title(titles[i] if len(titles) > i else '')
    plt.show()

def stylise_frames(hub_module, input_frame_path, style_frame_path, content_img_size, style_img_size):
    """
    Stylize input and style frames using a pre-trained model.

    Parameters:
    - hub_module: TensorFlow Hub module for style transfer.
    - input_frame_path: Path to the input frame.
    - style_frame_path: Path to the style frame.
    - content_img_size: Desired size for the content image.
    - style_img_size: Desired size for the style image.

    Returns:
    - Stylized image.
    """
    content_image = load_image(input_frame_path, content_img_size)
    style_image = load_image(style_frame_path, style_img_size, crop=True)
    style_image = tf.nn.avg_pool(style_image, ksize=[3, 3], strides=[1, 1], padding='SAME')
    outputs = hub_module(tf.constant(content_image), tf.constant(style_image))
    stylized_image = outputs[0]
    return stylized_image

def save_tensor_image(tensor, output_path):
    """
    Save a tensor image to a file.

    Parameters:
    - tensor: Tensor image to save.
    - output_path: Path to save the image.

    Returns:
    - None
    """
    si_np = tensor.numpy()
    si_np = np.squeeze(si_np, axis=0)
    si_np = (si_np * 255).astype(np.uint8)
    im1 = PIL.Image.fromarray(si_np, 'RGB')
    im1.save(output_path)
