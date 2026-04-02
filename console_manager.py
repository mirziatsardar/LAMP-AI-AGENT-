import json
import os
from typing import List, Dict, Optional
from icmplib import ping
from settings import CONSOLES_CONFIG_PATH, CONFIG_DIR, DEFAULT_ARTNET_PORT, DEFAULT_OSC_PORT

class Console:
    """Lighting Console Model"""
    def __init__(self, name: str, ip: str, protocol: str = "artnet", 
                 universe: int = 0, artnet_port: int = DEFAULT_ARTNET_PORT, 
                 osc_port: int = DEFAULT_OSC_PORT, osc_prefix: str = "/"):
        self.name = name
        self.ip = ip
        self.protocol = protocol.lower()
        self.universe = universe
        self.artnet_port = artnet_port
        self.osc_port = osc_port
        self.osc_prefix = osc_prefix
        self.is_online = False
    
    def ping(self, timeout: float = 1.0, count: int = 2) -> bool:
        """Ping console to check connectivity"""
        try:
            response = ping(self.ip, count=count, timeout=timeout)
            self.is_online = response.is_alive
            return self.is_online
        except Exception:
            self.is_online = False
            return False
    
    def to_dict(self) -> Dict:
        """Convert console to dictionary for saving"""
        return {
            "name": self.name,
            "ip": self.ip,
            "protocol": self.protocol,
            "universe": self.universe,
            "artnet_port": self.artnet_port,
            "osc_port": self.osc_port,
            "osc_prefix": self.osc_prefix
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Console':
        """Create console from dictionary"""
        return Console(
            name=data["name"],
            ip=data["ip"],
            protocol=data.get("protocol", "artnet"),
            universe=data.get("universe", 0),
            artnet_port=data.get("artnet_port", DEFAULT_ARTNET_PORT),
            osc_port=data.get("osc_port", DEFAULT_OSC_PORT),
            osc_prefix=data.get("osc_prefix", "/")
        )


class ConsoleManager:
    """Manager for Lighting Consoles"""
    def __init__(self):
        self.consoles: List[Console] = []
        self.active_console: Optional[Console] = None
        self._load_config()
    
    def _ensure_config_dir(self) -> None:
        """Ensure config directory exists"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
    
    def _load_config(self) -> None:
        """Load consoles from config file"""
        self._ensure_config_dir()
        if os.path.exists(CONSOLES_CONFIG_PATH):
            try:
                with open(CONSOLES_CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    self.consoles = [Console.from_dict(item) for item in data]
            except Exception:
                self.consoles = []
    
    def _save_config(self) -> None:
        """Save consoles to config file"""
        self._ensure_config_dir()
        try:
            with open(CONSOLES_CONFIG_PATH, "w") as f:
                json.dump([c.to_dict() for c in self.consoles], f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def add_console(self, console: Console) -> bool:
        """Add new console to manager"""
        for existing in self.consoles:
            if existing.name.lower() == console.name.lower():
                print(f"Console '{console.name}' already exists")
                return False
        self.consoles.append(console)
        self._save_config()
        return True
    
    def remove_console(self, name: str) -> bool:
        """Remove console by name"""
        original_len = len(self.consoles)
        self.consoles = [c for c in self.consoles if c.name.lower() != name.lower()]
        
        if self.active_console and self.active_console.name.lower() == name.lower():
            self.active_console = None
        
        if len(self.consoles) < original_len:
            self._save_config()
            return True
        return False
    
    def get_console(self, name: str) -> Optional[Console]:
        """Get console by name"""
        for console in self.consoles:
            if console.name.lower() == name.lower():
                return console
        return None
    
    def set_active_console(self, name: str) -> bool:
        """Set active console by name"""
        console = self.get_console(name)
        if console:
            self.active_console = console
            return True
        print(f"Console '{name}' not found")
        return False
    
    def ping_all_consoles(self) -> None:
        """Ping all consoles to check connectivity"""
        print("\n--- Pinging All Consoles ---")
        for console in self.consoles:
            status = "Online" if console.ping() else "Offline"
            print(f"{console.name} ({console.ip}): {status}")
        print("-----------------------------\n")
    
    def list_consoles(self) -> None:
        """List all configured consoles"""
        if not self.consoles:
            print("No consoles configured")
            return
        
        print("\n--- Configured Consoles ---")
        for i, console in enumerate(self.consoles, 1):
            active_marker = "*" if self.active_console and self.active_console.name == console.name else " "
            status = "Online" if console.is_online else "Offline"
            print(f"{active_marker} {i}. {console.name} - {console.ip} - Protocol: {console.protocol.upper()} - {status}")
        print("----------------------------\n")
