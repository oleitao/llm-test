import base64
import os
import streamlit as st

def get_image_base64(image_path):
    """Convert image to base64 string for embedding in HTML"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return None

def load_header_image_advanced():
    """
    Advanced image loading with multiple strategies for production deployment
    """
    # Strategy 1: Try direct Streamlit image loading
    image_paths = [
        "header.jpg",
        "header.jpeg", 
        "./header.jpg",
        "./header.jpeg",
        "/app/header.jpg",
        "/app/header.jpeg"
    ]
    
    for image_path in image_paths:
        try:
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
                return True
        except Exception:
            continue
    
    # Strategy 2: Try base64 embedding
    for image_path in image_paths:
        try:
            if os.path.exists(image_path):
                img_base64 = get_image_base64(image_path)
                if img_base64:
                    # Determine file extension for proper MIME type
                    ext = image_path.split('.')[-1].lower()
                    mime_type = f"image/{ext}" if ext in ['jpg', 'jpeg', 'png', 'gif'] else "image/jpeg"
                    
                    st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 20px;">
                        <img src="data:{mime_type};base64,{img_base64}" 
                             style="width: 100%; max-width: 600px; height: auto; border-radius: 10px;">
                    </div>
                    """, unsafe_allow_html=True)
                    return True
        except Exception:
            continue
    
    # Strategy 3: Fallback to styled text header
    st.markdown("""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <h1 style="color: white; margin: 0; font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">🚀</h1>
        <h1 style="color: white; margin: 10px 0; font-size: 2.5em; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">Elon Musk AI Chatbot</h1>
        <p style="color: #f0f8ff; margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">Powered by Advanced RAG Technology & Vector Search</p>
        <p style="color: #e6f3ff; margin: 5px 0 0 0; font-size: 1em; opacity: 0.8;">Ask questions about Elon Musk's tweets and get intelligent responses</p>
    </div>
    """, unsafe_allow_html=True)
    return False
