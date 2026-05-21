"""
Streamlit Frontend
Simple UI for testing the creative generation workflow
"""
import streamlit as st
import requests
import json
from pathlib import Path
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Pixora - Creative Engine",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"

# Header
st.title("🎨 Pixora Creative Engine")
st.markdown("AI-Powered Product Creative Generation for E-commerce Brands")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_url = st.text_input("API Base URL", value=API_BASE_URL)
    st.markdown("---")
    st.markdown("### 📖 About")
    st.info(
        "Pixora generates AI marketing creatives:\n"
        "• 5 Product Images\n"
        "• 2 Product Videos\n"
        "• Creative Strategy\n"
        "• Brand Alignment Checks"
    )


# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Generate", "📦 Bulk Upload", "📊 Dashboard", "📚 API Docs"])


# ==================== Tab 1: Single Generation ====================

with tab1:
    st.header("Generate Creatives for Single Product")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        product_url = st.text_input(
            "Product URL",
            placeholder="https://example.com/product",
            help="Enter a valid e-commerce product URL"
        )
    
    with col2:
        st.write("")
        st.write("")
        generate_btn = st.button("🚀 Generate", use_container_width=True, key="single_gen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_override = st.text_input("Brand Override (optional)", placeholder="Custom Brand Name")
    
    with col2:
        target_audience = st.text_input("Target Audience (optional)", placeholder="e.g., Young professionals")
    
    if generate_btn:
        if not product_url:
            st.error("❌ Please enter a product URL")
        else:
            with st.spinner("🔄 Generating creatives... This may take 2-5 minutes"):
                try:
                    # Call API
                    response = requests.post(
                        f"{api_url}/api/v1/generate",
                        json={
                            "url": product_url,
                            "brand_override": brand_override if brand_override else None,
                            "target_audience": target_audience if target_audience else None
                        },
                        timeout=600
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display results
                        st.success("✅ Creatives generated successfully!")
                        
                        # Product Data
                        st.subheader("📦 Product Information")
                        col1, col2, col3 = st.columns(3)
                        
                        product = result.get("product_data", {})
                        with col1:
                            st.metric("Title", product.get("title", "N/A")[:30])
                        with col2:
                            st.metric("Price", f"${product.get('price', 'N/A')}")
                        with col3:
                            st.metric("Rating", f"⭐ {product.get('rating', 'N/A')}/5")
                        
                        # Creative Brief
                        st.subheader("💡 Creative Strategy")
                        brief = result.get("creative_brief", {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Target Audience:**")
                            st.write(brief.get("target_audience", "N/A"))
                            
                            st.write("**Visual Themes:**")
                            for theme in brief.get("visual_themes", []):
                                st.write(f"• {theme}")
                        
                        with col2:
                            st.write("**Marketing Hooks:**")
                            for hook in brief.get("hooks", [])[:3]:
                                st.write(f"• {hook}")
                            
                            st.write("**Color Palette:**")
                            for color in brief.get("color_palette", []):
                                st.write(f"• {color}")
                        
                        # Generated Images
                        st.subheader("🖼️ Generated Images")
                        images = result.get("images", [])
                        
                        if images:
                            cols = st.columns(3)
                            for idx, image in enumerate(images):
                                with cols[idx % 3]:
                                    st.write(f"**Image {idx + 1}**")
                                    st.caption(image.get("prompt", "")[:100])
                                    st.info(f"Quality: {image.get('quality_score', 0):.0%}")
                        else:
                            st.warning("No images generated")
                        
                        # Generated Videos
                        st.subheader("🎬 Generated Videos")
                        videos = result.get("videos", [])
                        
                        if videos:
                            for idx, video in enumerate(videos):
                                st.write(f"**Video {idx + 1}**")
                                st.caption(video.get("script", "")[:150])
                                st.info(f"Duration: {video.get('duration', 0):.1f}s")
                        else:
                            st.warning("No videos generated")
                        
                        # Quality Review
                        st.subheader("✅ Quality Review")
                        review = result.get("critic_review", {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            score = review.get("overall_quality", 0)
                            st.metric("Overall Quality", f"{score:.0%}", delta=None)
                        with col2:
                            score = review.get("hallucination_score", 0)
                            st.metric("Accuracy", f"{score:.0%}")
                        with col3:
                            score = review.get("consistency_score", 0)
                            st.metric("Consistency", f"{score:.0%}")
                        with col4:
                            score = review.get("branding_score", 0)
                            st.metric("Branding", f"{score:.0%}")
                        
                        if review.get("issues"):
                            st.warning("**Issues found:**")
                            for issue in review.get("issues", []):
                                st.write(f"• {issue}")
                        
                        if review.get("suggestions"):
                            st.info("**Suggestions:**")
                            for suggestion in review.get("suggestions", []):
                                st.write(f"• {suggestion}")
                        
                        # Processing time
                        processing_time = result.get("total_processing_time", 0)
                        st.success(f"⏱️ Processing completed in {processing_time:.1f} seconds")
                    
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the backend is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ==================== Tab 2: Bulk Upload ====================

with tab2:
    st.header("Bulk Processing - Upload CSV")
    
    st.markdown("""
    Upload a CSV file with multiple product URLs. Format:
    ```
    url,brand_override,custom_themes
    https://product1.com,Brand1,modern;minimalist
    https://product2.com,Brand2,luxury;elegant
    ```
    """)
    
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file:
        st.write(f"📄 File: {uploaded_file.name}")
        
        # Preview
        with st.expander("Preview CSV"):
            import pandas as pd
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
        
        if st.button("🚀 Start Batch Processing", use_container_width=True):
            uploaded_file.seek(0)
            
            with st.spinner("📤 Uploading batch..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file)}
                    response = requests.post(
                        f"{api_url}/api/v1/bulk-generate",
                        files=files,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        job_id = result.get("job_id")
                        
                        st.success(f"✅ Batch job created: {job_id}")
                        st.info(f"Processing {result.get('total_urls')} products...")
                        
                        # Store job_id for polling
                        st.session_state.batch_job_id = job_id
                        
                        # Status placeholder
                        status_placeholder = st.empty()
                        progress_placeholder = st.empty()
                        
                        # Poll for status
                        while True:
                            status_response = requests.get(
                                f"{api_url}/api/v1/bulk-job/{job_id}",
                                timeout=10
                            )
                            
                            if status_response.status_code == 200:
                                status = status_response.json()
                                progress = status.get("progress", 0)
                                
                                with progress_placeholder.container():
                                    st.progress(progress / 100)
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Status", status.get("status", "unknown").upper())
                                    with col2:
                                        st.metric("Processed", status.get("processed_urls", 0))
                                    with col3:
                                        st.metric("Failed", status.get("failed_urls", 0))
                                
                                if status.get("status") in ["completed", "failed"]:
                                    break
                            
                            time.sleep(2)  # Poll every 2 seconds
                    
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ==================== Tab 3: Dashboard ====================

with tab3:
    st.header("📊 Processing Dashboard")
    
    st.markdown("**Active Jobs & Status Tracking**")
    
    if st.button("🔄 Refresh Status"):
        st.rerun()
    
    # Health check
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend API is running")
        else:
            st.error("❌ Backend API error")
    except:
        st.error("❌ Cannot connect to backend API")
    
    st.info("Dashboard would show active jobs, processing queue, and statistics in production version")


# ==================== Tab 4: API Docs ====================

with tab4:
    st.header("📚 API Documentation")
    
    st.subheader("Endpoints")
    
    st.markdown("""
    ### Single Product Generation
    ```
    POST /api/v1/generate
    
    Request:
    {
        "url": "https://product-url.com",
        "brand_override": "Brand Name (optional)",
        "target_audience": "Target Description (optional)",
        "custom_themes": ["theme1", "theme2"] (optional)
    }
    
    Response:
    {
        "product_data": {...},
        "creative_brief": {...},
        "prompts": {...},
        "images": [...],
        "videos": [...],
        "critic_review": {...},
        "total_processing_time": 120.5,
        "status": "success"
    }
    ```
    
    ### Bulk Processing
    ```
    POST /api/v1/bulk-generate
    
    Upload CSV file with urls
    
    Response:
    {
        "job_id": "abc123",
        "status": "queued",
        "total_urls": 5,
        "message": "Batch processing started"
    }
    ```
    
    ### Check Job Status
    ```
    GET /api/v1/job/{job_id}
    GET /api/v1/bulk-job/{job_id}
    ```
    """)
    
    st.subheader("System Architecture")
    st.image("https://via.placeholder.com/800x400?text=System+Architecture", use_column_width=True)


# Footer
st.markdown("---")
st.markdown("🎨 **Pixora v1.0** | AI Product Creative Generation Engine")
