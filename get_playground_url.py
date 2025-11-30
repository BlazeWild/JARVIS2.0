"""
Simple script to get the LiveKit Playground URL for your agent
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

sandbox_id = "digital-syscall-116ehj"

def get_playground_url():
    """Get the LiveKit Playground URL with token"""
    try:
        # Get connection details from sandbox
        token_endpoint = "https://cloud-api.livekit.io/api/sandbox/connection-details"
        headers = {"X-Sandbox-ID": sandbox_id}
        
        response = requests.get(token_endpoint, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            server_url = data['serverUrl']
            token = data['participantToken']
            
            # Construct playground URL
            # Extract domain from wss URL
            domain = server_url.replace('wss://', '').replace('ws://', '')
            
            playground_url = f"https://{domain}/custom/playground?token={token}"
            
            print("=" * 80)
            print("🎉 LIVEKIT PLAYGROUND URL")
            print("=" * 80)
            print()
            print("Copy this URL and paste in your browser:")
            print()
            print(playground_url)
            print()
            print("=" * 80)
            print("This is the OFFICIAL LiveKit UI with:")
            print("✅ Automatic voice detection")
            print("✅ No buttons needed")
            print("✅ Full interruption support")
            print("✅ Clean, professional interface")
            print("=" * 80)
            print()
            print("🚀 Your agent is already running on LiveKit's cloud (FREE)")
            print("💡 No CPU/memory usage on your machine")
            print()
            
            return playground_url
            
        else:
            print(f"❌ Failed to get token: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    get_playground_url()
