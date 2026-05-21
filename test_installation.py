#!/usr/bin/env python3
"""
Test script to verify Pixora installation and API connectivity
"""
import sys
import requests
import subprocess
from pathlib import Path

def test_python():
    """Check Python version"""
    print("🔍 Testing Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}")
        return True
    print(f"❌ Python 3.8+ required (found {version.major}.{version.minor})")
    return False

def test_dependencies():
    """Check if dependencies are installed"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'pydantic',
        'requests', 'playwright', 'beautifulsoup4', 'groq'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def test_directories():
    """Check if required directories exist"""
    print("\n🔍 Testing directories...")
    
    dirs = ['outputs', 'outputs/images', 'outputs/videos', 'logs']
    
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}")
        else:
            print(f"❌ {dir_path} - MISSING")
            path.mkdir(parents=True, exist_ok=True)
            print(f"   Created {dir_path}")
    
    return True

def test_env_file():
    """Check environment file"""
    print("\n🔍 Testing environment configuration...")
    
    env_file = Path('.env')
    if env_file.exists():
        print("✓ .env file exists")
        
        # Check for required keys
        content = env_file.read_text()
        required_keys = ['GROQ_API_KEY']
        
        missing_keys = [key for key in required_keys if key not in content]
        
        if missing_keys:
            print(f"⚠️  Missing required keys in .env: {', '.join(missing_keys)}")
            return False
        
        return True
    else:
        print("❌ .env file not found")
        print("   Copy from .env.example:")
        print("   cp .env.example .env")
        return False

def test_api_health():
    """Test if API is running"""
    print("\n🔍 Testing API connectivity...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✓ API is running on http://localhost:8000")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  API not running on http://localhost:8000")
        print("   Start with: python -m api.main")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Pixora Installation Test Suite")
    print("=" * 50)
    
    results = {
        "Python": test_python(),
        "Dependencies": test_dependencies(),
        "Directories": test_directories(),
        "Environment": test_env_file(),
        "API": test_api_health(),
    }
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✓" if result else "❌"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! System is ready to use.")
    else:
        failed = [name for name, result in results.items() if not result]
        print(f"❌ Some tests failed: {', '.join(failed)}")
        print("\nNext steps:")
        print("1. Fix failed tests above")
        print("2. Start API: python -m api.main")
        print("3. Start frontend: streamlit run frontend/app.py")
        print("4. Run tests again to verify")
    
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
