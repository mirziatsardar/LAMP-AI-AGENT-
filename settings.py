import os

# Configuration File Paths
CONFIG_DIR = "./config"
CONSOLES_CONFIG_PATH = os.path.join(CONFIG_DIR, "consoles.json")
FIXTURES_CONFIG_PATH = os.path.join(CONFIG_DIR, "fixtures.json")

# Default Protocol Ports
DEFAULT_ARTNET_PORT = 6454
DEFAULT_OSC_PORT = 8000

# Audio Processing Settings
AUDIO_SAMPLE_RATE = 44100
AUDIO_BLOCKSIZE = 1024
AUDIO_LOOPBACK = True  # Capture system output audio (no microphone needed)
BEAT_DETECTION_THRESHOLD = 0.15
BEAT_DETECTION_RELEASE_TIME = 0.3
LOW_FREQ_BAND = (20, 200)  # Bass range for beat detection

# DMX Settings
MAX_DMX_CHANNELS = 512
DEFAULT_UNIVERSE = 0
