import subprocess
import json

# PowerShell script to query Windows Management Instrumentation for the GPU memory
ps_script = """
Get-CimInstance Win32_VideoController | 
Select-Object Name, AdapterRAM | 
ConvertTo-Json
"""

try:
    result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
    
    # Handle empty or invalid output safely
    if not result.stdout.strip():
        print("No GPU data returned from Windows. Try running the script as Administrator.")
        exit()
        
    data = json.loads(result.stdout)
    
    # Handle both single GPU and multi-GPU setups (like an Intel/AMD integrated CPU + 5500M discrete GPU)
    gpus = data if isinstance(data, list) else [data]
    
    print("--- Detected GPUs ---")
    for gpu in gpus:
        name = gpu.get("Name", "Unknown GPU")
        ram_bytes = gpu.get("AdapterRAM", 0)
        
        # Windows sometimes gives negative or massive underflow integers for high VRAM cards due to a legacy 32-bit bug.
        # We take the absolute value or filter out standard integrated graphics fallbacks.
        vram_gb = abs(int(ram_bytes)) / (1024**3)
        
        print(f"GPU Name:   {name}")
        print(f"Total VRAM: {vram_gb:.2f} GB\n")

except Exception as e:
    print(f"Could not retrieve VRAM: {e}")
