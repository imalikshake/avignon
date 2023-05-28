import cv2
import matplotlib.pylab as plt
import numpy as np

def load_image(image_path, cvt="BGR2RGB"):
    image = cv2.imread(image_path)
    if cvt:
        color_p = getattr(cv2, f"COLOR_{cvt}")
        image = cv2.cvtColor(image, color_p)
    return image

def show_image(image, fig_size=(10,20)):
    image = np.squeeze(image)
    plt.figure(figsize=fig_size)
    plt.imshow(image)
    plt.axis('off')
    return plt.show()

def save_image(image_path, image, cvt="RGB2BGR"):
    if cvt:
        color_p = getattr(cv2,  f"COLOR_{cvt}")
        image = cv2.cvtColor(image, color_p)
    return cv2.imwrite(image_path, image)

def subtract(image1, image2):
    blended_image = cv2.subtract(image1, image2)
    return blended_image

def add(image1, image2):
    blended_image = cv2.add(image1, image2)
    return blended_image

def screen(image1, image2):
    inverted_image1 = cv2.bitwise_not(image1)
    inverted_image2 = cv2.bitwise_not(image2)
    blended_image = cv2.bitwise_not(cv2.multiply(inverted_image1, inverted_image2))
    return blended_image

def multiply(image1, image2):
    blended_image = cv2.multiply(image1, image2)
    return blended_image

def overlay(image1, image2, threshold=0.5):
    blended_image = cv2.addWeighted(image1, threshold, image2, 0.5, 0)
    # blended_image = np.where(image1 < threshold, 2 * image1 * image2, 1 - 2 * (1 - image1) * (1 - image2))
    return blended_image

def overlay_glitch(image1, image2, threshold=0.5):
    # blended_image = cv2.addWeighted(image1, threshold, image2, 0.5, 0)
    blended_image = np.where(image1 < threshold, 2 * image1 * image2, 1 - 2 * (1 - image1) * (1 - image2))
    return blended_image

def edges(image, min_g=1, max_g=4):
    edges = cv2.Canny(image, min_g, max_g)  # Adjust the threshold values for desired edge detection
    return edges

def interpolate(image1, image2, num_frames=10):
    interpolated_frames = []
    interpolation_step = 1 / (num_frames + 1)
    for i in range(1, num_frames + 1):
        interpolation_factor = i * interpolation_step
        interpolated_frame = cv2.addWeighted(image1, interpolation_factor, image2, 1 - interpolation_factor, 0)
        interpolated_frames.append(interpolated_frame)
    return interpolated_frames


def weighted_image(image, weight):
    image = image.astype(np.float32)
    image = image * weight
    image = image.astype(np.uint8)
    return image

def apply_filter(image, blue_multiplier=1.5, red_multiplier=0.7, green_multiplier=1):
    # Create a copy of the image
    filtered_image = image.copy()

    # Apply the cold filter by adjusting the color channels
    filtered_image[:, :, 2] = np.clip(filtered_image[:, :, 2] * blue_multiplier, 0, 255)  # Blue channel
    filtered_image[:, :, 1] = np.clip(filtered_image[:, :, 1] * green_multiplier, 0, 255)  # Red channel
    filtered_image[:, :, 0] = np.clip(filtered_image[:, :, 0] * red_multiplier, 0, 255)  # Red channel

    return filtered_image

def adjust_brightness_contrast(image, brightness=0, contrast=0):
    # Increase brightness
    # image = image.astype(np.float32)
    image = cv2.convertScaleAbs(image, alpha=1.0, beta=brightness)
    # image = image * contrast
    # image = image.astype(np.uint8)
    # Increase contrast
    if contrast > 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)
        image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)

    return image

def add_color_jitter(image, jitter_range):
    h, w, _ = image.shape
    jitter = np.random.uniform(-jitter_range, jitter_range, size=(h, w, 3)).astype(np.int16)

    jittered_image = image.astype(np.int16) + jitter
    jittered_image = np.clip(jittered_image, 0, 255).astype(np.uint8)
    return jittered_image


