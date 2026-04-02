from abc import ABC, abstractmethod
from typing import Dict, List

class Fixture(ABC):
    """Base class for all lighting fixtures"""
    def __init__(self, name: str, start_address: int, universe: int = 0):
        self.name = name
        self.start_address = start_address
        self.universe = universe
        self.channel_map: Dict[str, int] = {}
        self.channel_values: Dict[str, int] = {}
    
    @abstractmethod
    def render(self, dmx_buffer: List[int]) -> None:
        """Render fixture values to DMX buffer"""
        pass
    
    def set_dimmer(self, value: float) -> None:
        """Set dimmer level (0.0 to 1.0)"""
        if "dimmer" in self.channel_map:
            self.channel_values["dimmer"] = max(0, min(255, int(value * 255)))
    
    def set_color(self, r: float, g: float, b: float, w: float = 0.0) -> None:
        """Set RGBW color (0.0 to 1.0 per channel)"""
        if "red" in self.channel_map:
            self.channel_values["red"] = max(0, min(255, int(r * 255)))
        if "green" in self.channel_map:
            self.channel_values["green"] = max(0, min(255, int(g * 255)))
        if "blue" in self.channel_map:
            self.channel_values["blue"] = max(0, min(255, int(b * 255)))
        if "white" in self.channel_map:
            self.channel_values["white"] = max(0, min(255, int(w * 255)))
    
    def set_strobe(self, rate: float) -> None:
        """Set strobe rate (0.0 = no strobe, 1.0 = max rate)"""
        if "strobe" in self.channel_map:
            self.channel_values["strobe"] = max(0, min(255, int(rate * 255)))


class ParLight(Fixture):
    """Standard RGBW Par Can Light"""
    def __init__(self, name: str, start_address: int, universe: int = 0, has_white_channel: bool = True):
        super().__init__(name, start_address, universe)
        self.channel_map = {
            "dimmer": 0,
            "red": 1,
            "green": 2,
            "blue": 3
        }
        if has_white_channel:
            self.channel_map["white"] = 4
        for channel in self.channel_map:
            self.channel_values[channel] = 0
    
    def render(self, dmx_buffer: List[int]) -> None:
        for channel_name, offset in self.channel_map.items():
            channel_index = self.start_address - 1 + offset
            if 0 <= channel_index < len(dmx_buffer):
                dmx_buffer[channel_index] = self.channel_values[channel_name]


class WashLight(Fixture):
    """RGBW Wash Light with Color Temperature Control"""
    def __init__(self, name: str, start_address: int, universe: int = 0):
        super().__init__(name, start_address, universe)
        self.channel_map = {
            "dimmer": 0,
            "red": 1,
            "green": 2,
            "blue": 3,
            "white": 4,
            "color_temp": 5,
            "strobe": 6
        }
        for channel in self.channel_map:
            self.channel_values[channel] = 0
    
    def set_color_temperature(self, value: float) -> None:
        """Set color temperature (0.0 = warm, 1.0 = cool)"""
        self.channel_values["color_temp"] = max(0, min(255, int(value * 255)))
    
    def render(self, dmx_buffer: List[int]) -> None:
        for channel_name, offset in self.channel_map.items():
            channel_index = self.start_address - 1 + offset
            if 0 <= channel_index < len(dmx_buffer):
                dmx_buffer[channel_index] = self.channel_values[channel_name]


class MovingHead(Fixture):
    """Standard Moving Head Fixture with Pan/Tilt/RGBW/Gobo/Prism"""
    def __init__(self, name: str, start_address: int, universe: int = 0):
        super().__init__(name, start_address, universe)
        self.channel_map = {
            "pan": 0,
            "pan_fine": 1,
            "tilt": 2,
            "tilt_fine": 3,
            "dimmer": 4,
            "strobe": 5,
            "red": 6,
            "green": 7,
            "blue": 8,
            "white": 9,
            "gobo": 10,
            "focus": 11,
            "prism": 12
        }
        for channel in self.channel_map:
            self.channel_values[channel] = 0
    
    def set_pan_tilt(self, pan: float, tilt: float) -> None:
        """Set pan/tilt position (0.0 to 1.0 full range)"""
        self.channel_values["pan"] = max(0, min(255, int(pan * 255)))
        self.channel_values["tilt"] = max(0, min(255, int(tilt * 255)))
    
    def set_gobo(self, gobo_index: int) -> None:
        """Set gobo pattern (0 to 15)"""
        self.channel_values["gobo"] = max(0, min(255, gobo_index * 16))
    
    def set_prism(self, enabled: bool) -> None:
        """Enable/disable prism effect"""
        self.channel_values["prism"] = 255 if enabled else 0
    
    def set_focus(self, value: float) -> None:
        """Set focus (0.0 to 1.0)"""
        self.channel_values["focus"] = max(0, min(255, int(value * 255)))
    
    def render(self, dmx_buffer: List[int]) -> None:
        for channel_name, offset in self.channel_map.items():
            channel_index = self.start_address - 1 + offset
            if 0 <= channel_index < len(dmx_buffer):
                dmx_buffer[channel_index] = self.channel_values[channel_name]


class StrobeLight(Fixture):
    """High-Power Strobe Light"""
    def __init__(self, name: str, start_address: int, universe: int = 0):
        super().__init__(name, start_address, universe)
        self.channel_map = {
            "dimmer": 0,
            "strobe_rate": 1,
            "strobe_duration": 2
        }
        for channel in self.channel_map:
            self.channel_values[channel] = 0
    
    def set_strobe_rate(self, rate: float) -> None:
        """Set strobe rate (0.0 to 1.0)"""
        self.channel_values["strobe_rate"] = max(0, min(255, int(rate * 255)))
    
    def set_strobe_duration(self, duration: float) -> None:
        """Set flash duration (0.0 to 1.0)"""
        self.channel_values["strobe_duration"] = max(0, min(255, int(duration * 255)))
    
    def render(self, dmx_buffer: List[int]) -> None:
        for channel_name, offset in self.channel_map.items():
            channel_index = self.start_address - 1 + offset
            if 0 <= channel_index < len(dmx_buffer):
                dmx_buffer[channel_index] = self.channel_values[channel_name]


# Fixture Type Registry for Easy Extension
FIXTURE_TYPE_REGISTRY = {
    "par": ParLight,
    "wash": WashLight,
    "moving_head": MovingHead,
    "strobe": StrobeLight
}
