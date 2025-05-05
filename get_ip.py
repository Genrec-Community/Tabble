import socket

def get_ip_address():
    """Get the local IP address of the machine."""
    print("Starting IP address detection...")
    try:
        # Create a socket connection to an external server
        print("Creating socket connection...")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        print("Connecting to Google DNS (8.8.8.8)...")
        s.connect(("8.8.8.8", 80))
        print("Getting local socket name...")
        ip_address = s.getsockname()[0]
        s.close()
        print(f"Successfully detected IP: {ip_address}")
        return ip_address
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return "127.0.0.1"  # Return localhost if there's an error

if __name__ == "__main__":
    print("\nStarting Tabble IP detection...")
    ip = get_ip_address()
    print("\nYour IP Address:", ip)
    print(f"\nYou can access the Tabble app at: http://{ip}:8000\n")
    print("Share this URL with other devices on your network to access the application.")
    print("Note: Make sure your firewall allows incoming connections on port 8000.")
