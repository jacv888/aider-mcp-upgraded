import platform
from datetime import datetime

def main():
    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
    system_info = platform.platform()
    print(f"aider-mcp reconnected successfully!\nTimestamp: {timestamp}\nSystem Info: {system_info}")

if __name__ == "__main__":
    main()
