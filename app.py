# -*- coding: utf-8 -*-
"""Untitled12.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FLl_XqaqehdkgclipmQ0RgYqfTVTWZSQ
"""
import streamlit as st
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import json
import numpy as np
import matplotlib.pyplot as plt
from torchvision import models

# Set page config
st.set_page_config(page_title="Brain Tumor Classifier", layout="centered")

# Title
st.title("🧠 Brain Tumor MRI Classification")
st.markdown("Upload a brain MRI scan to predict the tumor type with confidence scores.")

# Load class names
with open("class_names.json", "r") as f:
    class_names = json.load(f)

# Define ResNet18 model (used during training)
def get_resnet_model(num_classes):
    model = models.resnet18(pretrained=False)
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(512, num_classes)
    )
    return model

# Load model
model = get_resnet_model(num_classes=len(class_names))
model.load_state_dict(torch.load("best_brain_tumor_model.pth", map_location=torch.device("cpu")))
model.eval()

# Define transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# File uploader
uploaded_file = st.file_uploader("📤 Upload a brain MRI image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="🖼 Uploaded MRI Image", use_column_width=True)

    # Preprocess image
    img_tensor = transform(image).unsqueeze(0)  # Add batch dimension

    # Predict
    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probs, 1)

    # Output
    st.markdown(f"### ✅ **Predicted Tumor Type:** `{class_names[predicted.item()]}`")
    st.markdown(f"### 📊 **Confidence Score:** `{confidence.item() * 100:.2f}%`")

    # Probability bar chart
    st.subheader("🔍 Prediction Confidence for All Classes")
    prob_np = probs[0].numpy()
    fig, ax = plt.subplots()
    ax.barh(class_names, prob_np * 100, color="#1f77b4")
    ax.set_xlabel("Confidence (%)")
    ax.set_xlim(0, 100)
    st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("Made by Mukta Londhe ")
