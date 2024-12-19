
import os
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import faiss
import numpy as np
import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions
from tqdm import tqdm
import logging

from api.models import Product, ProductImage, Category
from api.product.product_serializers import ProductSerializer

from rest_framework import serializers

logger = logging.getLogger(__name__)

response = requests.get(IMAGENET_LABELS_URL)
if response.status_code == 200:
    imagenet_labels = response.text.splitlines()
else:
    imagenet_labels = []
    print("Không thể tải nhãn lớp ImageNet.")

# ImageNet to Category Mapping
IMAGENET_TO_CATEGORY = {
    'Clothing': [454, 455, 456, 457, 458, 459, 460, 504],  # Thêm 'suit' (ví dụ: class 504)
    'Watch': [437],  # Wristwatch
    'Trouser': [461, 462],  # Jeans, Sweatpants
    'Shoes': [499, 500, 501, 502],  # Sandal, Sneaker
    'Bags': [414, 416]  # Handbag, Backpack
}

IMAGE_FOLDER = os.path.join(settings.MEDIA_ROOT, 'product_images')
TOP_K = 5

device = "cuda" 
print(f"Thiết bị sử dụng: {device}")

print("Tải mô hình ResNet-50 cho feature extraction...")
from torchvision.models import ResNet50_Weights
resnet = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])  
resnet = resnet.to(device)
resnet.eval()

print("Tải mô hình ResNet-50 cho classification...")
resnet_classifier = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1).to(device)
resnet_classifier.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

print("Tải hình ảnh từ thư mục...")
def load_images(image_folder):
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    image_paths = [os.path.join(image_folder, fname) for fname in os.listdir(image_folder)
                  if fname.lower().endswith(supported_formats)]
    return image_paths

def preprocess_images_resnet(image_paths, transform, device):
    images = []
    valid_image_paths = []
    for path in tqdm(image_paths, desc="Loading and preprocessing images"):
        try:
            image = Image.open(path).convert('RGB')
            image = transform(image).unsqueeze(0)
            images.append(image)
            valid_image_paths.append(path)
        except Exception as e:
            print(f"Không thể tải hình ảnh {path}: {e}")
    if images:
        images = torch.cat(images, dim=0).to(device)
    else:
        images = None
    return images, valid_image_paths

print("Tạo embeddings cho các hình ảnh...")
image_paths = load_images(IMAGE_FOLDER)
images, valid_image_paths = preprocess_images_resnet(image_paths, transform, device)

if images is None:
    print("Không có hình ảnh hợp lệ để xử lý.")
    image_embeddings = np.array([])
    faiss_index = None
else:
    with torch.no_grad():
        image_embeddings = resnet(images).cpu().numpy().reshape(images.size(0), -1)
    image_embeddings /= np.linalg.norm(image_embeddings, axis=1, keepdims=True)
    print("Xây dựng chỉ mục FAISS...")
    faiss_index = faiss.IndexFlatIP(image_embeddings.shape[1])
    faiss_index.add(image_embeddings)
    print(f"Chỉ mục FAISS đã chứa {faiss_index.ntotal} vectors.")

def classify_image(image, model, transform, device):
    """Phân loại hình ảnh vào category."""
    image = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        top_class = probabilities.argmax(dim=1).item()
        top_prob = probabilities[0][top_class].item()
    
    if imagenet_labels and top_class < len(imagenet_labels):
        top_label = imagenet_labels[top_class]
        print(f"Predicted Class Index: {top_class}, Label: {top_label}, Probability: {top_prob:.4f}")
    else:
        top_label = "Unknown"
        print(f"Predicted Class Index: {top_class}, Label: {top_label}, Probability: {top_prob:.4f}")
    
    for category, indices in IMAGENET_TO_CATEGORY.items():
        if top_class in indices:
            return category
    return "Unknown"

class ImageSearchView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]  

    def post(self, request, format=None):
        if 'image' not in request.FILES:
            return JsonResponse({"detail": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        query_image = request.FILES['image']
        try:
            image = Image.open(query_image).convert('RGB')
            image_tensor = transform(image).unsqueeze(0).to(device)
        except Exception as e:
            return JsonResponse({"detail": f"Invalid image file. Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        category = classify_image(image, resnet_classifier, transform, device)
        print(f"Category dự đoán: {category}")
        
        if category == "Unknown":
            return JsonResponse({
                "category": category,
                "products": []
            }, status=status.HTTP_200_OK)
        
        with torch.no_grad():
            query_embedding = resnet(image_tensor).cpu().numpy().reshape(1, -1)
            query_embedding /= np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        if faiss_index is None or faiss_index.ntotal == 0:
            return JsonResponse({"detail": "No images available for search."}, status=status.HTTP_404_NOT_FOUND)
        
        distances, indices = faiss_index.search(query_embedding, TOP_K)
        similar_images = [valid_image_paths[idx] for idx in indices[0]]
        
        products_set = set()
        for img_path in similar_images:
            try:
                relative_path = os.path.relpath(img_path, settings.MEDIA_ROOT)
                product_image = ProductImage.objects.get(image=relative_path)
                product = product_image.product
                if product.category and product.category.name == category:
                    products_set.add(product)
            except ProductImage.DoesNotExist:
                continue
            except Product.DoesNotExist:
                continue
        
        products = list(products_set)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        
        return JsonResponse({
            "category": category,
            "products": serializer.data
        }, status=status.HTTP_200_OK)
