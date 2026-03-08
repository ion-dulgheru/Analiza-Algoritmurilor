"""
CUDA Diagnostic Script - Run this first to check your setup
"""
import sys
import subprocess

print("=" * 60)
print("CUDA/GPU DIAGNOSTIC TOOL")
print("=" * 60)

# Check Python version
print(f"\n1. Python Version: {sys.version}")

# Check for NVIDIA GPU using nvidia-smi
print("\n2. Checking for NVIDIA GPU...")
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✓ NVIDIA GPU detected!")
        print(result.stdout.split('\n')[8:12])  # Show GPU info lines
        
        # Try to get CUDA version from nvidia-smi
        for line in result.stdout.split('\n'):
            if 'CUDA Version' in line:
                print(f"✓ {line.strip()}")
    else:
        print("✗ nvidia-smi command failed")
except FileNotFoundError:
    print("✗ nvidia-smi not found - NVIDIA drivers may not be installed")
except Exception as e:
    print(f"✗ Error running nvidia-smi: {e}")

# Check for CUDA toolkit installation
print("\n3. Checking for CUDA Toolkit...")
try:
    result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✓ CUDA Toolkit found!")
        print(result.stdout)
    else:
        print("✗ CUDA Toolkit not found in PATH")
except FileNotFoundError:
    print("✗ nvcc not found - CUDA Toolkit may not be installed or not in PATH")
except Exception as e:
    print(f"✗ Error: {e}")

# Check CuPy installation
print("\n4. Checking CuPy...")
try:
    import cupy as cp
    print(f"✓ CuPy installed: version {cp.__version__}")
    try:
        # Try to actually use CuPy
        test = cp.array([1, 2, 3])
        print(f"✓ CuPy GPU test successful!")
        print(f"  GPU: {cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}")
    except Exception as e:
        print(f"✗ CuPy installed but cannot access GPU: {e}")
except ImportError:
    print("✗ CuPy not installed")

# Check PyTorch installation
print("\n5. Checking PyTorch...")
try:
    import torch
    print(f"✓ PyTorch installed: version {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  CUDA version: {torch.version.cuda}")
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
except ImportError:
    print("✗ PyTorch not installed")

# Recommendations
print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)

has_gpu = False
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
    has_gpu = result.returncode == 0
except:
    pass

if not has_gpu:
    print("\n⚠ No NVIDIA GPU detected or drivers not installed")
    print("  → Install NVIDIA GPU drivers from: https://www.nvidia.com/drivers")
    print("  → Then reboot your system")
else:
    print("\n✓ GPU detected! Choose one of these options:")
    print("\nOption 1: PyTorch (RECOMMENDED - easiest setup)")
    print("  pip uninstall cupy-cuda12x")
    print("  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
    
    print("\nOption 2: CuPy (requires CUDA Toolkit)")
    print("  1. Install CUDA Toolkit 12.x from: https://developer.nvidia.com/cuda-downloads")
    print("  2. Add CUDA to PATH (usually C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.x\\bin)")
    print("  3. Reboot")
    print("  4. Keep cupy-cuda12x")
    
    print("\nOption 3: Run on CPU (no GPU)")
    print("  pip uninstall cupy-cuda12x")
    print("  Use the CPU version of the script")

print("\n" + "=" * 60)
input("Press Enter to exit...")
