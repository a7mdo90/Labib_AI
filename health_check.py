"""
Health Check Script for Labib Bot
سكريبت فحص الصحة لبوت لبيب
"""

import os
import sys
import time
import requests
from datetime import datetime
from config import Config

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment configuration...")
    
    try:
        Config.validate()
        print("✅ Environment configuration: OK")
        return True
    except ValueError as e:
        print(f"❌ Environment configuration failed: {e}")
        return False

def check_database():
    """Check database connectivity"""
    print("🗄️ Checking database connectivity...")
    
    try:
        import chromadb
        client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        collections = client.list_collections()
        print(f"✅ Database connectivity: OK ({len(collections)} collections)")
        return True
    except Exception as e:
        print(f"❌ Database connectivity failed: {e}")
        return False

def check_openai():
    """Check OpenAI API connectivity"""
    print("🤖 Checking OpenAI API...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("✅ OpenAI API: OK")
        return True
    except Exception as e:
        print(f"❌ OpenAI API failed: {e}")
        return False

def check_google_vision():
    """Check Google Vision API"""
    print("👁️ Checking Google Vision API...")
    
    try:
        if os.path.exists(Config.GOOGLE_APPLICATION_CREDENTIALS):
            print("✅ Google Vision credentials: Found")
            return True
        else:
            print(f"❌ Google Vision credentials not found: {Config.GOOGLE_APPLICATION_CREDENTIALS}")
            return False
    except Exception as e:
        print(f"❌ Google Vision API check failed: {e}")
        return False

def check_telegram():
    """Check Telegram bot token"""
    print("📱 Checking Telegram bot configuration...")
    
    if Config.TELEGRAM_TOKEN:
        print("✅ Telegram bot token: OK")
        return True
    else:
        print("❌ Telegram bot token: Missing")
        return False

def check_file_permissions():
    """Check file permissions"""
    print("📁 Checking file permissions...")
    
    try:
        # Check if we can write to the current directory
        test_file = "health_check_test.tmp"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        
        # Check if we can access the chroma store
        if os.access(Config.CHROMA_DB_PATH, os.R_OK | os.W_OK):
            print("✅ File permissions: OK")
            return True
        else:
            print(f"❌ Cannot access chroma store: {Config.CHROMA_DB_PATH}")
            return False
    except Exception as e:
        print(f"❌ File permissions check failed: {e}")
        return False

def check_system_resources():
    """Check system resources"""
    print("💻 Checking system resources...")
    
    try:
        import psutil
        
        # Check memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        print(f"📊 Memory usage: {memory_percent:.1f}%")
        
        # Check disk space
        disk = psutil.disk_usage('.')
        disk_percent = disk.percent
        print(f"💾 Disk usage: {disk_percent:.1f}%")
        
        if memory_percent > 90:
            print("⚠️ Warning: High memory usage")
        if disk_percent > 90:
            print("⚠️ Warning: High disk usage")
            
        print("✅ System resources: OK")
        return True
    except ImportError:
        print("⚠️ psutil not available, skipping system resource check")
        return True
    except Exception as e:
        print(f"❌ System resource check failed: {e}")
        return False

def main():
    """Main health check function"""
    print("🏥 Labib Bot Health Check")
    print("=" * 40)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Environment: {Config.ENVIRONMENT}")
    print()
    
    checks = [
        ("Environment", check_environment),
        ("Database", check_database),
        ("OpenAI API", check_openai),
        ("Google Vision", check_google_vision),
        ("Telegram Bot", check_telegram),
        ("File Permissions", check_file_permissions),
        ("System Resources", check_system_resources),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
            print()
        except Exception as e:
            print(f"❌ {name} check crashed: {e}")
            results.append((name, False))
            print()
    
    # Summary
    print("📋 Health Check Summary")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
    
    print()
    print(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All health checks passed! The bot is ready to run.")
        return 0
    else:
        print("⚠️ Some health checks failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
