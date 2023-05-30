import cv2
import matplotlib.pylab as plt
import numpy as np


def load_image(image_path, cvt="BGR2RGB"):
    """
    Load an image from the given file path.

    Parameters:
    - image_path: Path to the image file.
    - cvt: Color conversion flag. Default is "BGR2RGB" (convert from BGR to RGB).

    Returns:
    - Loaded image.
    """
    image = cv2.imread(image_path)
    if cvt:
        color_p = getattr(cv2, f"COLOR_{cvt}")
        image = cv2.cvtColor(image, color_p)
    return image

def show_image(image, fig_size=(10,20)):
    """
    Display the given image.

    Parameters:
    - image: Image to display.
    - fig_size: Figure size for the plot. Default is (10, 20).

    Returns:
    - None
    """
    image = np.squeeze(image)
    plt.figure(figsize=fig_size)
    plt.imshow(image)
    plt.axis('off')
    return plt.show()

def save_image(image_path, image, cvt="RGB2BGR"):
    """
    Save the given image to the specified file path.

    Parameters:
    - image_path: Path to save the image.
    - image: Image to save.
    - cvt: Color conversion flag. Default is "RGB2BGR" (convert from RGB to BGR).

    Returns:
    - Boolean indicating success (True) or failure (False) of saving the image.
    """
    if cvt:
        color_p = getattr(cv2,  f"COLOR_{cvt}")
        image = cv2.cvtColor(image, color_p)
    return cv2.imwrite(image_path, image)

def subtract(image1, image2):
    """
    Subtract image2 from image1.

    Parameters:
    - image1: First input image.
    - image2: Second input image.

    Returns:
    - Resulting subtracted image.
    """
    blended_image = cv2.subtract(image1, image2)
    return blended_image

def add(image1, image2):
    """
    Add image1 and image2.

    Parameters:
    - image1: First input image.
    - image2: Second input image.

    Returns:
    - Resulting added image.
    """
    blended_image = cv2.add(image1, image2)
    return blended_image

def screen(image1, image2):
    """
    Perform screen blending of image1 and image2.

    Parameters:
    - image1: First input image.
    - image2: Second input image.

    Returns:
    - Resulting screen blended image.
    """
    inverted_image1 = cv2.bitwise_not(image1)
    inverted_image2 = cv2.bitwise_not(image2)
    blended_image = cv2.bitwise_not(cv2.multiply(inverted_image1, inverted_image2))
    return blended_image

def multiply(image1, image2):
    """
    Perform multiply blending of image1 and image2.

    Parameters:
    - image1: First input image.
    - image2: Second input image.

    Returns:
    - Resulting multiplied image.
    """
    blended_image = cv2.multiply(image1, image2)
    return blended_image

def overlay(image1, image2, threshold=0.5):
    """
    Perform overlay blending of image1 and image2.

    Parameters:
    - image1: First input image.
    - image2: Second input image.
    - threshold: Threshold value for the blending. Default is 0.5.

    Returns:
    - Resulting overlay blended image.
    """
    blended_image = cv2.addWeighted(image1, threshold, image2, 0.5, 0)
    return blended_image

def overlay_glitch(image1, image2, threshold=0.5):
    """
    Perform overlay glitch blending of image1 and image2.

    Parameters:
    - image1: First input image.
    - image2: Second input image.
    - threshold: Threshold value for the blending. Default is 0.5.

    Returns:
    - Resulting overlay glitch blended image.
    """
    blended_image = np.where(image1 < threshold, 2 * image1 * image2, 1 - 2 * (1 - image1) * (1 - image2))
    return blended_image

def edges(image, min_g=1, max_g=4):
    """
    Detect edges in the given image.

    Parameters:
    - image: Input image.
    - min_g: Minimum threshold value for edge detection. Default is 1.
    - max_g: Maximum threshold value for edge detection. Default is 4.

    Returns:
    - Image with detected edges.
    """
    edges = cv2.Canny(image, min_g, max_g)  # Adjust the threshold values for desired edge detection
    return edges

def interpolate(image1, image2, num_frames=10):
    """
    Interpolate between image1 and image2 to generate intermediate frames.

    Parameters:
    - image1: First input image.
    - image2: Second input image.
    - num_frames: Number of intermediate frames to generate. Default is 10.

    Returns:
    - List of interpolated frames.
    """
    interpolated_frames = []
    interpolation_step = 1 / (num_frames + 1)
    for i in range(1, num_frames + 1):
        interpolation_factor = i * interpolation_step
        interpolated_frame = cv2.addWeighted(image1, interpolation_factor, image2, 1 - interpolation_factor, 0)
        interpolated_frames.append(interpolated_frame)
    return interpolated_frames

def weighted_image(image, weight):
    """
    Apply a weight factor to the image.

    Parameters:
    - image: Input image.
    - weight: Weight factor to apply.

    Returns:
    - Weighted image.
    """
    image = image.astype(np.float32)
    image = image * weight
    image = image.astype(np.uint8)
    return image

def apply_filter(image, blue_multiplier=1.5, red_multiplier=0.7, green_multiplier=1):
    """
    Apply a color filter to the image.

    Parameters:
    - image: Input image.
    - blue_multiplier: Multiplier for the blue channel. Default is 1.5.
    - red_multiplier: Multiplier for the red channel. Default is 0.7.
    - green_multiplier: Multiplier for the green channel. Default is 1.

    Returns:
    - Filtered image.
    """
    # Create a copy of the image
    filtered_image = image.copy()

    # Apply the color filter by adjusting the color channels
    filtered_image[:, :, 2] = np.clip(filtered_image[:, :, 2] * blue_multiplier, 0, 255)  # Blue channel
    filtered_image[:, :, 1] = np.clip(filtered_image[:, :, 1] * green_multiplier, 0, 255)  # Green channel
    filtered_image[:, :, 0] = np.clip(filtered_image[:, :, 0] * red_multiplier, 0, 255)  # Red channel

    return filtered_image

def adjust_brightness_contrast(image, brightness=0, contrast=0):
    """
    Adjust the brightness and contrast of the image.

    Parameters:
    - image: Input image.
    - brightness: Amount of brightness adjustment. Default is 0.
    - contrast: Amount of contrast adjustment. Default is 0.

    Returns:
    - Adjusted image.
    """
    image = cv2.convertScaleAbs(image, alpha=1.0, beta=brightness)
    if contrast > 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)
        image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)

    return image

def add_color_jitter(image, jitter_range):
    """
    Add color jitter to the image.

    Parameters:
    - image: Input image.
    - jitter_range: Range of color jitter to apply.

    Returns:
    - Image with added color jitter.
    """
    h, w, _ = image.shape
    jitter = np.random.uniform(-jitter_range, jitter_range, size=(h, w, 3)).astype(np.int16)

    jittered_image = image.astype(np.int16) + jitter
    jittered_image = np.clip(jittered_image, 0, 255).astype(np.uint8)
    return jittered_image

