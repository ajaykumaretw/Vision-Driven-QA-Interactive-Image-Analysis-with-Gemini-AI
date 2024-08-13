from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
from base64 import b64encode
import io

# Attempt to import the Generative AI SDK
try:
    import google.generativeai as genai
except ImportError:
    st.error("Google Generative AI SDK not found. Ensure it's installed.")
    st.stop()

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    st.error("API key not found. Set GOOGLE_API_KEY in the .env file.")
    st.stop()

# Configure the Generative AI SDK
try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Configuration error: {e}")
    st.stop()

def generate_response(text, image):
    """Generate a response from the Gemini model."""
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = b64encode(buffered.getvalue()).decode('utf-8')
        
        # Create the content dictionary
        content = {
            'parts': [
                {'text': text},
                {'mime_type': 'image/png', 'data': image_base64}
            ]
        }

        # Generate content
        response = model.generate_content(content)

        # Extract the text from the first part
        if response and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                text_content = candidate.content.parts[0].text
                return text_content

        st.error("No valid response received.")
        return ""
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return ""

def process_image(uploaded_file):
    """Process the uploaded file."""
    try:
        return Image.open(uploaded_file)
    except Exception as e:
        st.error(f"Error opening image: {e}")
        st.stop()

# Streamlit app setup
st.title('Invoice Extractor')
st.header('Gemini Invoice Analyzer')

# Input fields
text_input = st.text_input("Enter text prompt:")
uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "png", "jpeg"])

# Show and process the image
if uploaded_file:
    image = process_image(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Analyze Invoice"):
        response = generate_response(text_input, image)
        st.subheader("Response:")
        st.write(response)
else:
    st.info("Upload an image file to start.")
