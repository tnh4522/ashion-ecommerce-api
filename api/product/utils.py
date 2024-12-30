# api/product/utils.py
import os
import requests
import time
import cv2
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

def get_api_keys():
    HUGGINGFACE_API_TOKEN = "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"
    REMOVE_BG_API_KEY = "UVitYT541MLxqDeveagXEAT9"
    return HUGGINGFACE_API_TOKEN, REMOVE_BG_API_KEY

def query_huggingface(prompt, api_token, max_retries=5):
    API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
    headers = {"Authorization": f"Bearer {api_token}"}
    payload = {"inputs": prompt, "parameters": {"num_inference_steps": 30, "guidance_scale": 7.5}}

    attempt = 0
    while attempt < max_retries:
        print(f"Generating image (Attempt {attempt + 1})...")
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            error_info = response.json()
            estimated_time = error_info.get("estimated_time", 60)
            print(f"Model not ready. Waiting {estimated_time} seconds...")
            time.sleep(estimated_time)
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
        attempt += 1
    print("Failed to generate image after several attempts.")
    return None

def remove_background(input_image_path, api_key, output_image_path='image_no_bg.png'):
    print("Removing background...")
    try:
        with open(input_image_path, 'rb') as img_file:
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': img_file},
                data={'size': 'auto'},
                headers={'X-Api-Key': api_key},
            )
        if response.status_code == requests.codes.ok:
            with open(output_image_path, 'wb') as out_file:
                out_file.write(response.content)
            print(f"Background removed and saved to: {output_image_path}")
            return output_image_path
        else:
            print(f"Background removal error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def place_image_on_background(background_path, overlay_path, output_path="final_output.png", scale=0.75):
    background = cv2.imread(background_path)
    overlay = cv2.imread(overlay_path, cv2.IMREAD_UNCHANGED)

    if background is None or overlay is None:
        print("Error reading images.")
        return None

    ol_h, ol_w = overlay.shape[:2]
    new_width = int(ol_w * scale)
    new_height = int(ol_h * scale)
    overlay_resized = cv2.resize(overlay, (new_width, new_height), interpolation=cv2.INTER_AREA)

    bg_h, bg_w, _ = background.shape
    ol_h, ol_w = overlay_resized.shape[:2]
    x_start = (bg_w - ol_w) // 2
    y_start = (bg_h - ol_h) // 2

    if overlay_resized.shape[2] == 4:
        alpha = overlay_resized[:, :, 3] / 255.0
        for c in range(3):
            background[y_start:y_start+ol_h, x_start:x_start+ol_w, c] = (
                alpha * overlay_resized[:, :, c] +
                (1 - alpha) * background[y_start:y_start+ol_h, x_start:x_start+ol_w, c]
            )
    else:
        background[y_start:y_start+ol_h, x_start:x_start+ol_w] = overlay_resized

    cv2.imwrite(output_path, background)
    print(f"Image saved to: {output_path}")
    return output_path

def generate_product_image(prompt, background_path):
    HUGGINGFACE_API_TOKEN, REMOVE_BG_API_KEY = get_api_keys()

    # Generate image from prompt
    image_bytes = query_huggingface(prompt, HUGGINGFACE_API_TOKEN)
    if not image_bytes:
        print("Failed to generate image.")
        return None

    # Save generated image temporarily
    temp_image_path = os.path.join(settings.MEDIA_ROOT, 'temp', f'generated_image_{timezone.now().timestamp()}.png')
    os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
    with open(temp_image_path, "wb") as f:
        f.write(image_bytes)
    print(f"Generated image saved to: {temp_image_path}")

    # Remove background
    final_overlay_path = os.path.join(settings.MEDIA_ROOT, 'temp', f'no_bg_image_{timezone.now().timestamp()}.png')
    removed_bg_image = remove_background(temp_image_path, REMOVE_BG_API_KEY, final_overlay_path)
    if not removed_bg_image:
        print("Failed to remove background.")
        return None

    # Place on background
    final_output_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', f'final_output_{timezone.now().timestamp()}.png')
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
    placed_image = place_image_on_background(background_path, removed_bg_image, final_output_path, scale=0.75)
    if not placed_image:
        print("Failed to place image on background.")
        return None

    # Clean up temporary images
    try:
        os.remove(temp_image_path)
        os.remove(removed_bg_image)
    except:
        pass

    return placed_image
