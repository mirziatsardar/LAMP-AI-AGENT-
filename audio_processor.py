import soundcard as sc
import numpy as np
import time
from typing import Callable
from settings import AUDIO_SAMPLE_RATE, AUDIO_BLOCKSIZE, AUDIO_LOOPBACK, BEAT_DETECTION_THRESHOLD, BEAT_DETECTION_RELEASE_TIME, LOW_FREQ_BAND

class AudioProcessor:
    """Audio processor for system output capture and beat detection"""
    def __init__(self, beat_callback: Callable[[], None]):
        self.beat_callback = beat_callback
        self.running = False
        self.last_beat_time = 0
        self.fft_window = np.hanning(AUDIO_BLOCKSIZE)
        
        try:
            self.speaker = sc.default_speaker()
            self.samplerate = AUDIO_SAMPLE_RATE
            self.blocksize = AUDIO_BLOCKSIZE
        except Exception as e:
            print(f"Failed to initialize audio device: {e}")
            self.speaker = None
    
    def _detect_beat(self, audio_data: np.ndarray) -> bool:
        """Detect beat using bass frequency energy analysis"""
        if len(audio_data.shape) > 1:
            audio_mono = np.mean(audio_data, axis=1)
        else:
            audio_mono = audio_data
        
        fft_data = np.fft.rfft(audio_mono * self.fft_window)
        fft_magnitude = np.abs(fft_data)
        fft_freqs = np.fft.rfftfreq(len(audio_mono), 1.0 / self.samplerate)
        
        low_freq_mask = (fft_freqs >= LOW_FREQ_BAND[0]) & (fft_freqs <= LOW_FREQ_BAND[1])
        low_freq_energy = np.mean(fft_magnitude[low_freq_mask])
        
        normalized_energy = low_freq_energy / np.max(fft_magnitude) if np.max(fft_magnitude) > 0 else 0
        current_time = time.time()
        time_since_last_beat = current_time - self.last_beat_time
        
        if normalized_energy > BEAT_DETECTION_THRESHOLD and time_since_last_beat > BEAT_DETECTION_RELEASE_TIME:
            self.last_beat_time = current_time
            return True
        return False
    
    def start_capture(self) -> None:
        """Start audio capture and beat detection"""
        if not self.speaker:
            print("No audio device available")
            return
        
        self.running = True
        print("Starting system audio loopback capture")
        
        try:
            with self.speaker.recorder(samplerate=self.samplerate, blocksize=self.blocksize, loopback=AUDIO_LOOPBACK) as recorder:
                while self.running:
                    audio_data = recorder.record(numframes=self.blocksize)
                    if self._detect_beat(audio_data):
                        self.beat_callback()
        except Exception as e:
            print(f"Audio capture error: {e}")
            self.running = False
    
    def stop_capture(self) -> None:
        """Stop audio capture"""
        self.running = False
        print("Stopped audio capture")
