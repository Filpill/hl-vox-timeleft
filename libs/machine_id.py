"""
Machine ID utility for Half-Life VOX TimeLEFT application.
Provides a stable, anonymous machine identifier across sessions.
"""

import platform
import subprocess
import uuid
import hashlib


def get_machine_id() -> str:
    """
    Get a unique, stable machine identifier.

    Strategy:
    1. Try to read system machine-id (Linux, macOS, Windows)
    2. Fallback to hashed MAC address if system ID unavailable

    Returns:
        16-character hexadecimal machine identifier
    """
    system = platform.system()

    # Linux: Read /etc/machine-id
    if system == "Linux":
        try:
            with open('/etc/machine-id', 'r') as f:
                machine_id = f.read().strip()
                # Hash it for privacy and truncate to 16 chars
                return hashlib.sha256(machine_id.encode()).hexdigest()[:16]
        except (FileNotFoundError, PermissionError):
            pass

    # macOS: Get IOPlatformUUID
    elif system == "Darwin":
        try:
            result = subprocess.run(
                ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'IOPlatformUUID' in line:
                    platform_uuid = line.split('"')[3]
                    return hashlib.sha256(platform_uuid.encode()).hexdigest()[:16]
        except (subprocess.SubprocessError, IndexError, FileNotFoundError):
            pass

    # Windows: Get system UUID
    elif system == "Windows":
        try:
            result = subprocess.run(
                ['wmic', 'csproduct', 'get', 'UUID'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                system_uuid = lines[1].strip()
                return hashlib.sha256(system_uuid.encode()).hexdigest()[:16]
        except (subprocess.SubprocessError, IndexError, FileNotFoundError):
            pass

    # Fallback: Hash MAC address
    mac_address = uuid.getnode()
    return hashlib.sha256(str(mac_address).encode()).hexdigest()[:16]


if __name__ == "__main__":
    # Test the machine ID generation
    machine_id = get_machine_id()
    print(f"Machine ID: {machine_id}")
    print(f"Length: {len(machine_id)}")
    print(f"System: {platform.system()}")
