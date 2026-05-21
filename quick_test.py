#!/usr/bin/env python3
"""
Quick test of the Pixora system without running the full server
"""
import sys
import asyncio
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from agents.research_agent import product_researcher

async def quick_test():
    """Quick test of product research agent"""
    
    print("=" * 60)
    print("Pixora Quick Test - Product Research Agent")
    print("=" * 60)
    print()
    
    # Test URL
    test_url = "https://www.amazon.com/Apple-AirPods-Latest-Model/dp/B07PYLT6DN"
    
    print(f"Testing with URL: {test_url}")
    print()
    
    try:
        print("🔍 Running product research agent...")
        result = await product_researcher.extract_product_info(test_url)
        
        if result.get("title") != "Product Unavailable":
            print("✅ Success! Product data extracted:")
            print()
            print(f"  Title: {result.get('title')}")
            print(f"  Brand: {result.get('brand')}")
            print(f"  Price: ${result.get('price', 'N/A')}")
            print(f"  Rating: {result.get('rating', 'N/A')}/5")
            print(f"  Features: {len(result.get('features', []))} found")
            print(f"  Images: {len(result.get('image_urls', []))} found")
            print()
            print("System is working correctly!")
            return True
        else:
            print("⚠️  Could not extract product data")
            print("This may be due to:")
            print("  - Invalid or inaccessible URL")
            print("  - Website blocking automated access")
            print("  - Network issues")
            return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print()
    success = asyncio.run(quick_test())
    print()
    print("=" * 60)
    
    if success:
        print("✅ Quick test passed! System is ready.")
        print()
        print("Next steps:")
        print("  1. Start backend: python -m api.main")
        print("  2. Start frontend: streamlit run frontend/app.py")
        print("  3. Open browser: http://localhost:8501")
    else:
        print("❌ Quick test failed. See errors above.")
    
    print("=" * 60)
    print()
