import sounddevice as sd
import numpy as np
import time
from typing import Callable
from settings import AUDIO_SAMPLE_RATE, AUDIO_BLOCKSIZE, BEAT_DETECTION_THRESHOLD, BEAT_DETECTION_RELEASE_TIME, LOW_FREQ_BAND

class AudioProcessor:
    """使用 sounddevice 实现系统音频 loopback + 鼓点检测"""
    def __init__(self, beat_callback: Callable[[], None]):
        self.beat_callback = beat_callback
        self.running = False
        self.last_beat_time = 0
        self.fft_window = np.hanning(AUDIO_BLOCKSIZE)
        
        try:
            self.samplerate = AUDIO_SAMPLE_RATE
            self.blocksize = AUDIO_BLOCKSIZE
            print("✅ sounddevice 初始化成功")
        except Exception as e:
            print(f"❌ sounddevice 初始化失败: {e}")
    
    def _detect_beat(self, audio_data: np.ndarray) -> bool:
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
        
        if normalized_energy > BEAT_DETECTION_THRESHOLD and (current_time - self.last_beat_time) > BEAT_DETECTION_RELEASE_TIME:
            self.last_beat_time = current_time
            return True
        return False
    
    def start_capture(self) -> None:
        self.running = True
        print("🎵 开始系统音频 loopback 抓取（无需麦克风）")
        
        try:
            with sd.InputStream(samplerate=self.samplerate, 
                              blocksize=self.blocksize,
                              channels=1, 
                              dtype='float32',
                              latency='low') as stream:
                while self.running:
                    audio_data, _ = stream.read(self.blocksize)
                    if self._detect_beat(audio_data):
                        self.beat_callback()
        except Exception as e:
            print(f"❌ 音频抓取异常: {e}")
            self.running = False
    
    def stop_capture(self) -> None:
        self.running = False
        print("⏹️ 音频抓取已停止")
