import cv2
import matplotlib.pylab as plt
import numpy as np

def load_image(image_path):
    # ext = image_path.split(".")[-1]
    # if ext == "jpg" or ext == "jpeg":
    #     image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    # else:
    #     image = cv2.imread(image_path)
    image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    return image

def show_image(image, fig_size=(10,20)):
    image = np.squeeze(image)
    plt.figure(figsize=fig_size)
    plt.imshow(image)
    plt.axis('off')
    return plt.show()

def save_image(image_path, image):
    return cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

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

