import socket
import struct
from pythonosc import udp_client
from typing import List

class ArtNetSender:
    """Art-Net DMX over Ethernet Sender"""
    def __init__(self, target_ip: str, port: int = 6454):
        self.target_ip = target_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence = 0
    
    def send_dmx(self, universe: int, dmx_data: List[int]) -> None:
        """Send DMX data to specified universe"""
        header = b"Art-Net\0"
        op_code = struct.pack('<H', 0x5000)
        protocol_version = struct.pack('>H', 14)
        sequence = struct.pack('B', self.sequence)
        physical = struct.pack('B', 0)
        sub_universe = struct.pack('B', universe & 0xFF)
        net = struct.pack('B', (universe >> 8) & 0x7F)
        length = struct.pack('>H', 512)
        
        dmx_bytes = bytes(dmx_data[:512])
        if len(dmx_bytes) < 512:
            dmx_bytes += b'\x00' * (512 - len(dmx_bytes))
        
        packet = header + op_code + protocol_version + sequence + physical + sub_universe + net + length + dmx_bytes
        self.socket.sendto(packet, (self.target_ip, self.port))
        self.sequence = (self.sequence + 1) % 256


class OSCSender:
    """Open Sound Control (OSC) Protocol Sender"""
    def __init__(self, target_ip: str, port: int = 8000):
        self.target_ip = target_ip
        self.port = port
        self.client = udp_client.SimpleUDPClient(target_ip, port)
    
    def send_message(self, address: str, *args) -> None:
        """Send OSC message to specified address"""
        self.client.send_message(address, args)
    
    def trigger_cue(self, cue_number: float) -> None:
        """Trigger lighting cue by number"""
        self.send_message("/cue/trigger", cue_number)
    
    def set_fader(self, fader_index: int, value: float) -> None:
        """Set fader level (0.0 to 1.0)"""
        self.send_message(f"/fader/{fader_index}", value)
    
    def blackout(self) -> None:
        """Trigger full blackout"""
        self.send_message("/blackout", 1)
    
    def release_blackout(self) -> None:
        """Release blackout"""
        self.send_message("/blackout", 0)
