import os
import asyncio
import cv2
import numpy as np
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from pdf2image import convert_from_bytes
from flask import Flask, render_template, request, jsonify
import pytesseract


app = Flask(__name__)

# Load the pre-trained TrOCR model and processor
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")

def preprocess_image(img):
    # Convert the PIL image to RGB format
    img = img.convert('RGB')
    
    # Convert the PIL image to numpy array
    img_np = np.array(img)
    
    # Preprocess the image using the TrOCR processor
    pixel_values = processor(images=img_np, return_tensors="pt").pixel_values
    
    return pixel_values

def extract_text(img):
    # Preprocess the image
    pixel_values = preprocess_image(img)
    
    # Perform text recognition using the TrOCR model
    generated_ids = model.generate(pixel_values)
    
    # Decode the generated text
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return generated_text

def process_image(file_path):
    try:
        # Read the image using OpenCV
        img = cv2.imread(file_path)
        
        # Extract text from the image
        extracted_text = extract_text(img)
        
        return extracted_text.strip()
    except Exception as e:
        error_message = f"Error occurred during image processing: {str(e)}"
        print(error_message)
        return error_message

def process_pdf(file_path):
    try:
        # Convert PDF to images
        images = convert_from_bytes(open(file_path, 'rb').read())
        
        text = ''
        for i, image in enumerate(images):
            # Convert the image to OpenCV format
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Extract text from the image
            extracted_text = extract_text(img)
            
            text += f'Page {i + 1}:\n{extracted_text}\n\n'
        
        return text.strip()
    except Exception as e:
        error_message = f"Error occurred during PDF processing: {str(e)}"
        print(error_message)
        return error_message

async def ocr_core(file_path):
    if file_path.lower().endswith('.pdf'):
        return await process_pdf(file_path)
    else:
        return await process_image(file_path)
    
async def extract_text(img):
    # Preprocess the image
    pixel_values = preprocess_image(img)
    
    # Perform text recognition using the TrOCR model
    generated_ids = model.generate(pixel_values, max_length=512)
    
    # Decode the generated text
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return generated_text

async def process_image(file_path):
    try:
        # Read the image using PIL
        img = Image.open(file_path)
        
        # Extract text from the image using Tesseract OCR
        extracted_text = pytesseract.image_to_string(img)
        
        return extracted_text.strip()
    except Exception as e:
        error_message = f"Error occurred during image processing: {str(e)}"
        print(error_message)
        return error_message

async def process_pdf(file_path):
    try:
        # Convert PDF to images
        images = convert_from_bytes(open(file_path, 'rb').read())
        
        text = ''
        for i, image in enumerate(images):
            # Extract text from each page using Tesseract OCR
            extracted_text = pytesseract.image_to_string(image)
            
            text += f'Page {i + 1}:\n{extracted_text}\n\n'
        
        return text.strip()
    except Exception as e:
        error_message = f"Error occurred during PDF processing: {str(e)}"
        print(error_message)
        return error_message

async def ocr_core(file_path):
    if file_path.lower().endswith('.pdf'):
        return await process_pdf(file_path)
    else:
        return await process_image(file_path) 