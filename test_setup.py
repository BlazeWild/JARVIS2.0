"""
Test script to verify audio setup before running the full app
"""

import pyaudio
import sys

def test_microphone():
    """Test if microphone can be accessed"""
    print("🎤 Testing microphone access...")
    
    try:
        p = pyaudio.PyAudio()
        
        # List all audio devices
        print("\n📋 Available audio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"  [{i}] {info['name']}")
            print(f"      Input channels: {info['maxInputChannels']}")
            print(f"      Output channels: {info['maxOutputChannels']}")
        
        # Try to open default microphone
        print("\n✅ Testing default microphone...")
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            input=True,
            frames_per_buffer=480
        )
        
        print("✅ Microphone access successful!")
        print("🎤 Recording for 2 seconds...")
        
        # Record for 2 seconds
        frames = []
        for i in range(0, int(48000 / 480 * 2)):
            data = stream.read(480)
            frames.append(data)
        
        print("✅ Recording successful!")
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        print("\n🎉 All audio tests passed! You're ready to run the app.")
        return True
        
    except ImportError:
        print("❌ PyAudio not installed!")
        print("   Run: pip install pipwin")
        print("   Then: pipwin install pyaudio")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check microphone is connected")
        print("  2. Grant microphone permissions in Windows settings")
        print("  3. Try selecting a different device index")
        return False


def test_livekit():
    """Test if LiveKit SDK is installed"""
    print("\n📦 Testing LiveKit SDK...")
    
    try:
        from livekit import rtc
        print("✅ LiveKit SDK installed correctly")
        return True
    except ImportError:
        print("❌ LiveKit SDK not installed!")
        print("   Run: pip install livekit")
        return False


def test_env():
    """Test if .env file is configured"""
    print("\n🔐 Testing environment configuration...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if url and api_key and api_secret:
            print("✅ Environment variables configured")
            print(f"   LiveKit URL: {url[:30]}...")
            return True
        else:
            print("❌ Missing environment variables in .env file")
            return False
            
    except ImportError:
        print("❌ python-dotenv not installed!")
        print("   Run: pip install python-dotenv")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Friday Voice Assistant - Setup Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Environment", test_env()))
    results.append(("LiveKit SDK", test_livekit()))
    results.append(("Microphone", test_microphone()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    if all(result[1] for result in results):
        print("\n🎉 All tests passed! Ready to run:")
        print("   python agent.py (in terminal 1)")
        print("   python voice_assistant_gui_auto.py (in terminal 2)")
    else:
        print("\n⚠️ Some tests failed. Fix the issues above before running the app.")
        sys.exit(1)
