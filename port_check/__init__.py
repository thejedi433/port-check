#!/usr/bin/env python3
"""Check if a port is open on a host."""

import socket
import sys


def check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open on a host.
    
    Args:
        host: Hostname or IP address
        port: Port number to check
        timeout: Connection timeout in seconds
    
    Returns:
        True if port is open, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except (socket.error, socket.gaierror) as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: port-check <host> <port> [timeout]")
        print("Example: port-check localhost 8080")
        return 1
    
    host = sys.argv[1]
    port_str = sys.argv[2]
    timeout = 2.0
    
    if len(sys.argv) >= 4:
        try:
            timeout = float(sys.argv[3])
        except ValueError:
            print(f"Error: Invalid timeout value: {sys.argv[3]}")
            return 1
    
    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")
    except ValueError as e:
        print(f"Error: Invalid port: {port_str} ({e})")
        return 1
    
    is_open = check_port(host, port, timeout)
    
    if is_open:
        print(f"✓ Port {port} is open on {host}")
        return 0
    else:
        print(f"✗ Port {port} is closed on {host}")
        return 1

