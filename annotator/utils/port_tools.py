import socket, time

def wait_for_port(host, port, timeout=10):
    """Wait until a port is open (Flask server ready)."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (OSError, ConnectionRefusedError):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for {host}:{port}")
            time.sleep(0.1)