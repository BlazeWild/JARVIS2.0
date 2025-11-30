"""
Simple Desktop UI for Friday Voice Assistant
Just opens and starts - no buttons, just talk!
"""

import asyncio
import tkinter as tk
from tkinter import scrolledtext, Canvas
import os
from datetime import datetime
from dotenv import load_dotenv
from livekit import rtc
import logging
import requests
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


class FridayUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Friday Voice Assistant")
        self.root.geometry("700x550")
        self.root.configure(bg='#0a0a0a')
        
        self.room = None
        self.is_connected = False
        self.sandbox_id = "digital-syscall-116ehj"
        self.mic_level = 0
        self.speaker_level = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(
            self.root,
            text="FRIDAY",
            font=("Arial", 28, "bold"),
            fg='#00ffff',
            bg='#0a0a0a'
        )
        title.pack(pady=15)
        
        # Status
        self.status = tk.Label(
            self.root,
            text="● Starting...",
            font=("Arial", 14),
            fg='#ffaa00',
            bg='#0a0a0a'
        )
        self.status.pack()
        
        # Audio visualization frame
        audio_frame = tk.Frame(self.root, bg='#0a0a0a')
        audio_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Microphone bar
        mic_frame = tk.Frame(audio_frame, bg='#0a0a0a')
        mic_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            mic_frame,
            text="🎤 Your Voice:",
            font=("Arial", 10),
            fg='#00ff00',
            bg='#0a0a0a',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.mic_canvas = Canvas(
            mic_frame,
            width=500,
            height=30,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.mic_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Speaker bar
        speaker_frame = tk.Frame(audio_frame, bg='#0a0a0a')
        speaker_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            speaker_frame,
            text="🔊 Friday:",
            font=("Arial", 10),
            fg='#00ffff',
            bg='#0a0a0a',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.speaker_canvas = Canvas(
            speaker_frame,
            width=500,
            height=30,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.speaker_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Log
        self.log = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=70,
            height=10,
            font=("Consolas", 9),
            bg='#1a1a1a',
            fg='#00ff00',
            state='disabled'
        )
        self.log.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Auto-connect
        self.root.after(100, lambda: asyncio.create_task(self.auto_connect()))
        
        # Start visualizer update
        self.update_visualizer()
        
    def log_msg(self, msg, color="#00ff00"):
        self.log.configure(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{timestamp}] ", "time")
        self.log.tag_config("time", foreground="#00aaff")
        self.log.insert(tk.END, f"{msg}\n")
        self.log.see(tk.END)
        self.log.configure(state='disabled')
        
    def update_visualizer(self):
        """Update audio level bars"""
        # Microphone bar (green)
        self.mic_canvas.delete("all")
        if self.mic_level > 0:
            width = int(500 * self.mic_level)
            self.mic_canvas.create_rectangle(
                0, 0, width, 30,
                fill='#00ff00',
                outline=''
            )
            
        # Speaker bar (cyan)
        self.speaker_canvas.delete("all")
        if self.speaker_level > 0:
            width = int(500 * self.speaker_level)
            self.speaker_canvas.create_rectangle(
                0, 0, width, 30,
                fill='#00ffff',
                outline=''
            )
            
        # Decay levels
        self.mic_level *= 0.85
        self.speaker_level *= 0.85
        
        # Schedule next update
        self.root.after(50, self.update_visualizer)
        
    async def get_token(self):
        try:
            response = requests.get(
                "https://cloud-api.livekit.io/api/sandbox/connection-details",
                headers={"X-Sandbox-ID": self.sandbox_id}
            )
            if response.status_code == 200:
                data = response.json()
                return data['serverUrl'], data['participantToken']
        except Exception as e:
            logger.error(f"Token error: {e}")
        return None, None
        
    async def auto_connect(self):
        self.log_msg("🚀 Connecting to Friday...")
        self.status.config(text="● Connecting...", fg="#ffaa00")
        
        server_url, token = await self.get_token()
        if not server_url:
            self.log_msg("❌ Connection failed")
            self.status.config(text="● Failed", fg="#ff4444")
            return
            
        self.room = rtc.Room()
        
        @self.room.on("participant_connected")
        def on_agent_joined(p):
            self.log_msg(f"✅ Friday joined")
            
        @self.room.on("track_subscribed")
        def on_audio(track, pub, participant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                self.log_msg("🔊 Receiving audio from Friday")
                audio_stream = rtc.AudioStream(track)
                asyncio.create_task(self.receive_audio(audio_stream))
                
        @self.room.on("data_received")
        def on_data(packet):
            try:
                msg = packet.data.decode('utf-8')
                self.log_msg(f"💬 Friday: {msg}", "#00ffff")
            except:
                pass
        
        try:
            await self.room.connect(server_url, token)
            self.is_connected = True
            self.status.config(text="● Live - Just Talk!", fg="#00ff00")
            self.log_msg("✅ Connected! Microphone is active - just speak naturally")
            self.log_msg("💡 You can interrupt Friday anytime")
            
            # CRITICAL: Wait a moment for room to be ready
            await asyncio.sleep(0.5)
            
            # Start mic IMMEDIATELY
            await self.start_mic()
            
        except Exception as e:
            self.log_msg(f"❌ Error: {e}")
            self.status.config(text="● Error", fg="#ff4444")
            logger.error(f"Connection error: {e}", exc_info=True)
            
    async def start_mic(self):
        try:
            import pyaudio
            
            # Test microphone first
            p = pyaudio.PyAudio()
            
            # List ALL devices
            self.log_msg("🎤 Available audio devices:")
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    self.log_msg(f"  [{i}] {info['name']} (inputs: {info['maxInputChannels']})")
            
            # Use device 2 (your working mic from console mode)
            device_index = 2
            device_info = p.get_device_info_by_index(device_index)
            self.log_msg(f"✅ Using device {device_index}: {device_info['name']}")
            
            p.terminate()
            
            # Create LiveKit audio source with correct settings
            self.audio_source = rtc.AudioSource(48000, 1)
            
            # Create track
            track = rtc.LocalAudioTrack.create_audio_track("mic", self.audio_source)
            
            # Publish options - CRITICAL for agent to receive
            options = rtc.TrackPublishOptions()
            options.source = rtc.TrackSource.SOURCE_MICROPHONE
            
            # Publish track
            publication = await self.room.local_participant.publish_track(track, options)
            
            self.log_msg(f"✅ Microphone track published: {publication.sid}")
            self.log_msg("🎤 Starting audio capture...")
            
            # Start capturing audio with the correct device
            asyncio.create_task(self.capture_audio(device_index))
            
        except Exception as e:
            self.log_msg(f"❌ Mic error: {e}")
            logger.error(f"Mic error: {e}", exc_info=True)
            
    async def capture_audio(self, device_index=2):
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            
            # Open microphone stream with SPECIFIC device
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                input=True,
                input_device_index=device_index,  # USE THE CORRECT DEVICE
                frames_per_buffer=480,
                stream_callback=None
            )
            
            self.log_msg("✅ Microphone capturing - SPEAK NOW!")
            
            frame_count = 0
            sent_count = 0
            
            while self.is_connected:
                try:
                    # Read audio from microphone
                    data = stream.read(480, exception_on_overflow=False)
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    
                    # Calculate audio level for visualization
                    level = np.abs(audio_array).mean() / 32768.0
                    
                    # Always update bar and send audio (not just when loud)
                    self.mic_level = min(1.0, level * 15)
                    
                    # Log occasionally
                    frame_count += 1
                    if frame_count % 100 == 0:
                        self.log_msg(f"🎤 Mic active - level: {level:.3f} - frames sent: {sent_count}")
                    
                    # Create audio frame for LiveKit
                    frame = rtc.AudioFrame(
                        data=audio_array.tobytes(),
                        sample_rate=48000,
                        num_channels=1,
                        samples_per_channel=480
                    )
                    
                    # Send to LiveKit - THIS IS CRITICAL
                    await self.audio_source.capture_frame(frame)
                    sent_count += 1
                    
                    # Small sleep to prevent blocking
                    await asyncio.sleep(0.001)
                    
                except Exception as read_error:
                    logger.error(f"Read error: {read_error}")
                    await asyncio.sleep(0.01)
                    
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.log_msg("🎤 Microphone stopped")
            
        except Exception as e:
            logger.error(f"Capture error: {e}", exc_info=True)
            self.log_msg(f"❌ Mic capture failed: {e}")
            
    async def receive_audio(self, audio_stream):
        """Receive and play audio from Friday with visualization"""
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            
            # Open output stream
            output_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=48000,
                output=True,
                frames_per_buffer=480
            )
            
            async for frame_event in audio_stream:
                # Get the actual frame from the event
                frame = frame_event.frame
                
                # Play audio
                output_stream.write(frame.data.tobytes())
                
                # Calculate level for visualization
                audio_array = np.frombuffer(frame.data.tobytes(), dtype=np.int16)
                level = np.abs(audio_array).mean() / 32768.0
                self.speaker_level = min(1.0, level * 10)
                
            output_stream.stop_stream()
            output_stream.close()
            p.terminate()
            
        except Exception as e:
            logger.error(f"Audio receive error: {e}")
            self.log_msg(f"❌ Speaker playback failed: {e}")


async def main():
    root = tk.Tk()
    app = FridayUI(root)
    
    while True:
        try:
            root.update()
            await asyncio.sleep(0.01)
        except tk.TclError:
            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
