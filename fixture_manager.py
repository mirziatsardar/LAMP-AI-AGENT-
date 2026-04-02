import json
import os
from typing import List, Dict, Optional
from fixtures import Fixture, FIXTURE_TYPE_REGISTRY
from settings import FIXTURES_CONFIG_PATH, CONFIG_DIR, MAX_DMX_CHANNELS, DEFAULT_UNIVERSE

class FixtureManager:
    """Manager for Lighting Fixtures"""
    def __init__(self):
        self.fixtures: List[Fixture] = []
        self.dmx_buffer: Dict[int, List[int]] = {DEFAULT_UNIVERSE: [0] * MAX_DMX_CHANNELS}
        self._load_config()
    
    def _ensure_config_dir(self) -> None:
        """Ensure config directory exists"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
    
    def _load_config(self) -> None:
        """Load fixtures from config file"""
        self._ensure_config_dir()
        if os.path.exists(FIXTURES_CONFIG_PATH):
            try:
                with open(FIXTURES_CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    for item in data:
                        fixture_type = item.get("type", "par")
                        if fixture_type in FIXTURE_TYPE_REGISTRY:
                            fixture_class = FIXTURE_TYPE_REGISTRY[fixture_type]
                            fixture = fixture_class(
                                name=item["name"],
                                start_address=item["start_address"],
                                universe=item.get("universe", DEFAULT_UNIVERSE)
                            )
                            self.fixtures.append(fixture)
            except Exception as e:
                print(f"Failed to load fixtures: {e}")
                self.fixtures = []
    
    def _save_config(self) -> None:
        """Save fixtures to config file"""
        self._ensure_config_dir()
        try:
            with open(FIXTURES_CONFIG_PATH, "w") as f:
                data = []
                for fixture in self.fixtures:
                    fixture_type = None
                    for type_name, cls in FIXTURE_TYPE_REGISTRY.items():
                        if isinstance(fixture, cls):
                            fixture_type = type_name
                            break
                    if fixture_type:
                        data.append({
                            "name": fixture.name,
                            "type": fixture_type,
                            "start_address": fixture.start_address,
                            "universe": fixture.universe
                        })
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save fixtures: {e}")
    
    def add_fixture(self, fixture: Fixture) -> bool:
        """Add new fixture with address conflict check"""
        for existing in self.fixtures:
            if existing.name.lower() == fixture.name.lower():
                print(f"Fixture '{fixture.name}' already exists")
                return False
        
        new_channels = set(range(fixture.start_address, fixture.start_address + len(fixture.channel_map)))
        for existing in self.fixtures:
            if existing.universe == fixture.universe:
                existing_channels = set(range(existing.start_address, existing.start_address + len(existing.channel_map)))
                if new_channels.intersection(existing_channels):
                    print(f"Address conflict with fixture '{existing.name}'")
                    return False
        
        self.fixtures.append(fixture)
        if fixture.universe not in self.dmx_buffer:
            self.dmx_buffer[fixture.universe] = [0] * MAX_DMX_CHANNELS
        self._save_config()
        return True
    
    def remove_fixture(self, name: str) -> bool:
        """Remove fixture by name"""
        original_len = len(self.fixtures)
        self.fixtures = [f for f in self.fixtures if f.name.lower() != name.lower()]
        
        if len(self.fixtures) < original_len:
            self._save_config()
            return True
        return False
    
    def get_fixture(self, name: str) -> Optional[Fixture]:
        """Get fixture by name"""
        for fixture in self.fixtures:
            if fixture.name.lower() == name.lower():
                return fixture
        return None
    
    def list_fixtures(self) -> None:
        """List all configured fixtures"""
        if not self.fixtures:
            print("No fixtures configured")
            return
        
        print("\n--- Configured Fixtures ---")
        for i, fixture in enumerate(self.fixtures, 1):
            fixture_type = None
            for type_name, cls in FIXTURE_TYPE_REGISTRY.items():
                if isinstance(fixture, cls):
                    fixture_type = type_name.upper()
                    break
            print(f"{i}. {fixture.name} - Type: {fixture_type} - Start Address: {fixture.start_address} - Universe: {fixture.universe}")
        print("----------------------------\n")
    
    def render_dmx(self) -> None:
        """Render all fixtures to DMX buffer"""
        for universe in self.dmx_buffer:
            self.dmx_buffer[universe] = [0] * MAX_DMX_CHANNELS
        
        for fixture in self.fixtures:
            if fixture.universe in self.dmx_buffer:
                fixture.render(self.dmx_buffer[fixture.universe])
    
    def clear_dmx(self) -> None:
        """Clear all DMX channels (full blackout)"""
        for universe in self.dmx_buffer:
            self.dmx_buffer[universe] = [0] * MAX_DMX_CHANNELS
        for fixture in self.fixtures:
            fixture.set_dimmer(0.0)
            fixture.set_color(0.0, 0.0, 0.0, 0.0)
            fixture.set_strobe(0.0)
