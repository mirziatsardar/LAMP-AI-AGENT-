import threading
import time
import random

from settings import DEFAULT_UNIVERSE
from console_manager import ConsoleManager, Console
from fixture_manager import FixtureManager
from fixtures import FIXTURE_TYPE_REGISTRY
from protocols import ArtNetSender, OSCSender
from audio_processor import AudioProcessor

# Global Managers
console_manager = ConsoleManager()
fixture_manager = FixtureManager()

# Global Protocol Senders
artnet_sender: ArtNetSender = None
osc_sender: OSCSender = None

# Global State
is_running_lighting = False
lighting_thread: threading.Thread = None
audio_processor: AudioProcessor = None

# Beat Detection Callback
def on_beat_detected():
    if not is_running_lighting:
        return
    
    r = random.random()
    g = random.random()
    b = random.random()
    w = random.random() * 0.5
    
    for fixture in fixture_manager.fixtures:
        fixture.set_color(r, g, b, w)
        fixture.set_dimmer(1.0)
        if hasattr(fixture, 'set_strobe_rate'):
            fixture.set_strobe_rate(random.random() * 0.8)
    
    fixture_manager.render_dmx()
    
    if artnet_sender and console_manager.active_console:
        universe = console_manager.active_console.universe
        if universe in fixture_manager.dmx_buffer:
            artnet_sender.send_dmx(universe, fixture_manager.dmx_buffer[universe])
    
    if osc_sender and console_manager.active_console:
        osc_sender.trigger_cue(random.randint(1, 10))

# Lighting Control Loop
def lighting_loop():
    global is_running_lighting
    print("Starting lighting control loop")
    
    while is_running_lighting:
        fixture_manager.render_dmx()
        if artnet_sender and console_manager.active_console:
            universe = console_manager.active_console.universe
            if universe in fixture_manager.dmx_buffer:
                artnet_sender.send_dmx(universe, fixture_manager.dmx_buffer[universe])
        time.sleep(0.03)
    
    fixture_manager.clear_dmx()
    if artnet_sender and console_manager.active_console:
        universe = console_manager.active_console.universe
        artnet_sender.send_dmx(universe, fixture_manager.dmx_buffer[universe])
    if osc_sender:
        osc_sender.blackout()
    
    print("Stopped lighting control loop")

# Initialize Protocol Senders
def initialize_senders():
    global artnet_sender, osc_sender
    
    if not console_manager.active_console:
        print("No active console selected")
        return False
    
    active_console = console_manager.active_console
    
    if active_console.protocol in ["artnet", "both"]:
        try:
            artnet_sender = ArtNetSender(active_console.ip, active_console.artnet_port)
            print(f"Art-Net sender initialized for {active_console.ip}:{active_console.artnet_port}")
        except Exception as e:
            print(f"Failed to initialize Art-Net: {e}")
            artnet_sender = None
    
    if active_console.protocol in ["osc", "both"]:
        try:
            osc_sender = OSCSender(active_console.ip, active_console.osc_port)
            print(f"OSC sender initialized for {active_console.ip}:{active_console.osc_port}")
        except Exception as e:
            print(f"Failed to initialize OSC: {e}")
            osc_sender = None
    
    return True

# Main Menu
def show_main_menu():
    print("\n===== UNIVERSAL LIGHTING CONTROL SYSTEM =====")
    print("1. List and Select Console")
    print("2. Add New Console")
    print("3. Remove Console")
    print("4. Ping All Consoles")
    print("5. List Fixtures")
    print("6. Add New Fixture")
    print("7. Remove Fixture")
    print("8. Start Audio Sync Lighting")
    print("9. Stop Lighting")
    print("10. Exit")
    print("===============================================")

# Menu Handlers
def select_console_menu():
    console_manager.list_consoles()
    if not console_manager.consoles:
        return
    choice = input("Enter console number to select: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(console_manager.consoles):
        print("Invalid choice")
        return
    selected = console_manager.consoles[int(choice) - 1]
    if console_manager.set_active_console(selected.name):
        print(f"Active console set to '{selected.name}'")
        initialize_senders()

def add_new_console_menu():
    print("\n--- Add New Console ---")
    name = input("Enter console name: ").strip()
    if not name:
        print("Console name cannot be empty")
        return
    
    ip = input("Enter console IP address: ").strip()
    if not ip:
        print("IP address cannot be empty")
        return
    
    print("\nSelect protocol:")
    print("1. Art-Net (Default)")
    print("2. OSC")
    print("3. Both")
    protocol_choice = input("Enter choice (1-3): ").strip()
    
    protocol = "artnet"
    if protocol_choice == "2":
        protocol = "osc"
    elif protocol_choice == "3":
        protocol = "both"
    
    universe = input(f"Enter universe (default {DEFAULT_UNIVERSE}): ").strip()
    universe = int(universe) if universe.isdigit() else DEFAULT_UNIVERSE
    
    artnet_port = input("Enter Art-Net port (default 6454): ").strip()
    artnet_port = int(artnet_port) if artnet_port.isdigit() else 6454
    
    osc_port = input("Enter OSC port (default 8000): ").strip()
    osc_port = int(osc_port) if osc_port.isdigit() else 8000
    
    osc_prefix = input("Enter OSC address prefix (default /): ").strip()
    osc_prefix = osc_prefix if osc_prefix else "/"
    
    console = Console(name, ip, protocol, universe, artnet_port, osc_port, osc_prefix)
    if console_manager.add_console(console):
        print(f"Console '{name}' added successfully")
    else:
        print("Failed to add console")

def add_new_fixture_menu():
    print("\n--- Add New Fixture ---")
    name = input("Enter fixture name: ").strip()
    if not name:
        print("Fixture name cannot be empty")
        return
    
    print("\nSelect fixture type:")
    for i, (type_name, _) in enumerate(FIXTURE_TYPE_REGISTRY.items(), 1):
        print(f"{i}. {type_name.upper()}")
    
    type_choice = input("Enter choice: ").strip()
    if not type_choice.isdigit() or int(type_choice) < 1 or int(type_choice) > len(FIXTURE_TYPE_REGISTRY):
        print("Invalid choice")
        return
    
    fixture_type = list(FIXTURE_TYPE_REGISTRY.keys())[int(type_choice) - 1]
    fixture_class = FIXTURE_TYPE_REGISTRY[fixture_type]
    
    start_address = input("Enter DMX start address (1-512): ").strip()
    if not start_address.isdigit() or int(start_address) < 1 or int(start_address) > 512:
        print("Invalid start address")
        return
    start_address = int(start_address)
    
    universe = input(f"Enter universe (default {DEFAULT_UNIVERSE}): ").strip()
    universe = int(universe) if universe.isdigit() else DEFAULT_UNIVERSE
    
    fixture = fixture_class(name, start_address, universe)
    if fixture_manager.add_fixture(fixture):
        print(f"Fixture '{name}' added successfully")
    else:
        print("Failed to add fixture")

def start_lighting():
    global is_running_lighting, lighting_thread, audio_processor
    
    if is_running_lighting:
        print("Lighting is already running")
        return
    if not console_manager.active_console:
        print("No active console selected")
        return
    if not console_manager.active_console.is_online:
        print("Active console is offline. Check connectivity.")
        return
    if not fixture_manager.fixtures:
        print("No fixtures configured")
        return
    
    audio_processor = AudioProcessor(on_beat_detected)
    if not audio_processor.speaker:
        print("Failed to initialize audio processor")
        return
    
    is_running_lighting = True
    lighting_thread = threading.Thread(target=lighting_loop)
    lighting_thread.daemon = True
    lighting_thread.start()
    
    audio_thread = threading.Thread(target=audio_processor.start_capture)
    audio_thread.daemon = True
    audio_thread.start()
    
    print("Audio sync lighting started successfully")

def stop_lighting():
    global is_running_lighting, audio_processor
    
    if not is_running_lighting:
        print("Lighting is not running")
        return
    
    is_running_lighting = False
    if audio_processor:
        audio_processor.stop_capture()
        audio_processor = None
    if lighting_thread and lighting_thread.is_alive():
        lighting_thread.join()
    
    print("Lighting stopped successfully")

# Main Program Loop
def main():
    print("Welcome to Universal Lighting Control System")
    print("Compatible with all DMX/Art-Net/OSC lighting consoles and fixtures")
    
    while True:
        show_main_menu()
        choice = input("Enter your choice (1-10): ").strip()
        
        if choice == "1":
            select_console_menu()
        elif choice == "2":
            add_new_console_menu()
        elif choice == "3":
            console_manager.list_consoles()
            name = input("Enter console name to remove: ").strip()
            if console_manager.remove_console(name):
                print(f"Console '{name}' removed successfully")
            else:
                print("Failed to remove console")
        elif choice == "4":
            console_manager.ping_all_consoles()
        elif choice == "5":
            fixture_manager.list_fixtures()
        elif choice == "6":
            add_new_fixture_menu()
        elif choice == "7":
            fixture_manager.list_fixtures()
            name = input("Enter fixture name to remove: ").strip()
            if fixture_manager.remove_fixture(name):
                print(f"Fixture '{name}' removed successfully")
            else:
                print("Failed to remove fixture")
        elif choice == "8":
            start_lighting()
        elif choice == "9":
            stop_lighting()
        elif choice == "10":
            print("Exiting program...")
            stop_lighting()
            break
        else:
            print("Invalid choice. Enter a number between 1 and 10.")

if __name__ == "__main__":
    main()
