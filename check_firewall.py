import subprocess
import sys
import os

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def check_firewall_rule():
    """Check if there's a firewall rule for port 8000."""
    try:
        if sys.platform == 'win32':
            # Windows
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=TabbleApp'],
                capture_output=True,
                text=True
            )
            return 'TabbleApp' in result.stdout
        else:
            # Linux/Mac
            result = subprocess.run(
                ['sudo', 'iptables', '-L', '-n'],
                capture_output=True,
                text=True
            )
            return '8000' in result.stdout
    except Exception as e:
        print(f"Error checking firewall rule: {e}")
        return False

def add_firewall_rule():
    """Add a firewall rule to allow incoming connections on port 8000."""
    try:
        if sys.platform == 'win32':
            # Windows
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                'name=TabbleApp',
                'dir=in',
                'action=allow',
                'protocol=TCP',
                'localport=8000'
            ], check=True)
            print("Firewall rule added successfully.")
        else:
            # Linux/Mac
            subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT', '-p', 'tcp', '--dport', '8000',
                '-j', 'ACCEPT'
            ], check=True)
            print("Firewall rule added successfully.")
    except Exception as e:
        print(f"Error adding firewall rule: {e}")
        print("Please manually add a firewall rule to allow incoming connections on port 8000.")

if __name__ == "__main__":
    print("\nChecking firewall settings for Tabble app...\n")
    
    if not is_admin():
        print("This script needs to be run with administrator privileges to check and modify firewall settings.")
        print("Please run it again as administrator/root.")
        sys.exit(1)
    
    if check_firewall_rule():
        print("Firewall rule for port 8000 already exists.")
    else:
        print("No firewall rule found for port 8000.")
        response = input("Would you like to add a firewall rule to allow incoming connections on port 8000? (y/n): ")
        
        if response.lower() == 'y':
            add_firewall_rule()
        else:
            print("\nNo changes made to firewall settings.")
            print("Note: Other devices on your network may not be able to access the Tabble app.")
    
    print("\nFirewall check complete.")
    print("If you're still having issues connecting from other devices, please check your network settings.")
    print("You may need to manually configure your firewall to allow incoming connections on port 8000.")
