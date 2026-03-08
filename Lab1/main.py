import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

print("=" * 60)
print("TAXI FARE REGRESSION - AUTO GPU/CPU")
print("=" * 60)

# Try to detect and use GPU, fallback to CPU gracefully
GPU_LIBRARY = None
device_name = "CPU"

# Try PyTorch first (better Windows support)
try:
    import torch
    if torch.cuda.is_available():
        GPU_LIBRARY = "pytorch"
        device_name = torch.cuda.get_device_name(0)
        print(f"✓ Using PyTorch with GPU: {device_name}")
    else:
        print("✓ PyTorch available but no GPU, using CPU")
        GPU_LIBRARY = "pytorch_cpu"
except ImportError:
    pass

# Try CuPy if PyTorch not available or no GPU
if GPU_LIBRARY is None:
    try:
        import cupy as cp
        # Test if CuPy can actually access GPU
        test = cp.array([1, 2, 3])
        _ = test + 1  # Force GPU operation
        GPU_LIBRARY = "cupy"
        device_name = cp.cuda.runtime.getDeviceProperties(0)['name'].decode()
        print(f"✓ Using CuPy with GPU: {device_name}")
    except Exception as e:
        if 'cupy' in str(e).lower() or 'cuda' in str(e).lower():
            print(f"⚠ CuPy installed but cannot access GPU: {str(e)[:80]}...")
        GPU_LIBRARY = None

# Fallback to NumPy CPU
if GPU_LIBRARY is None:
    print("✓ Using NumPy (CPU only)")
    print("  To enable GPU: see installation instructions below")

print("=" * 60)
print()

# Load data
df = pd.read_csv('chicago_taxi_train.csv')
print(f"Loaded {len(df)} samples")

# Training parameters
alpha = 0.01
iterations = 1000

# ============================================================================
# PYTORCH VERSION (GPU or CPU)
# ============================================================================
if GPU_LIBRARY in ["pytorch", "pytorch_cpu"]:
    x_np = df[["TRIP_MILES"]].to_numpy()
    y_np = df["FARE"].to_numpy()
    
    device = torch.device('cuda' if GPU_LIBRARY == "pytorch" else 'cpu')
    x = torch.from_numpy(x_np).float().to(device)
    y = torch.from_numpy(y_np).float().to(device)
    
    w = torch.tensor(0.0, device=device)
    b = torch.tensor(0.0, device=device)
    
    mse_history = []
    
    print("Training...")
    for i in range(iterations):
        y_pred = w * x + b
        mse = torch.mean((y_pred - y) ** 2)
        mse_history.append(mse.item())
        
        dw = torch.mean((y_pred - y) * x)
        db = torch.mean(y_pred - y)
        
        w -= alpha * dw
        b -= alpha * db
        
        print(f"Iteration {i+1}: w={w.item():.4f}, b={b.item():.4f}, MSE={mse.item():.4f}")
    
    # Convert back to NumPy for plotting
    x_plot = x.cpu().numpy()
    y_plot = y.cpu().numpy()
    w_final = w.item()
    b_final = b.item()

# ============================================================================
# CUPY VERSION (GPU)
# ============================================================================
elif GPU_LIBRARY == "cupy":
    x = cp.asarray(df[["TRIP_MILES"]].to_numpy())
    y = cp.asarray(df["FARE"].to_numpy())
    
    w, b = 0, 0
    mse_history = []
    
    print("Training...")
    for i in range(iterations):
        y_pred = w * x + b
        mse = cp.mean((y_pred - y) ** 2)
        mse_history.append(float(cp.asnumpy(mse)))
        
        dw = cp.mean((y_pred - y) * x)
        db = cp.mean(y_pred - y)
        
        w -= alpha * dw
        b -= alpha * db
        
        print(f"Iteration {i+1}: w={float(cp.asnumpy(w)):.4f}, b={float(cp.asnumpy(b)):.4f}, MSE={mse_history[-1]:.4f}")
    
    # Convert back to NumPy for plotting
    x_plot = cp.asnumpy(x)
    y_plot = cp.asnumpy(y)
    w_final = float(cp.asnumpy(w))
    b_final = float(cp.asnumpy(b))

# ============================================================================
# NUMPY VERSION (CPU FALLBACK)
# ============================================================================
else:
    x = df[["TRIP_MILES"]].to_numpy()
    y = df["FARE"].to_numpy()
    
    w, b = 0, 0
    mse_history = []
    
    print("Training...")
    for i in range(iterations):
        y_pred = w * x + b
        mse = np.mean((y_pred - y) ** 2)
        mse_history.append(float(mse))
        
        dw = np.mean((y_pred - y) * x)
        db = np.mean(y_pred - y)
        
        w -= alpha * dw
        b -= alpha * db
        
        print(f"Iteration {i+1}: w={float(w):.4f}, b={float(b):.4f}, MSE={mse_history[-1]:.4f}")
    
    x_plot = x
    y_plot = y
    w_final = float(w)
    b_final = float(b)

# ============================================================================
# PLOTTING
# ============================================================================
print(f"\n✓ Training complete on {device_name}")
print(f"  Final model: y = {w_final:.2f}x + {b_final:.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.scatter(x_plot, y_plot, color='blue', alpha=0.5, s=20, label='Actual')
x_line = np.array([x_plot.min(), x_plot.max()])
y_line = w_final * x_line + b_final
ax1.plot(x_line, y_line, 'r-', linewidth=2, label=f'Fitted line: y = {w_final:.2f}x + {b_final:.2f}')

ax1.set_xlabel('Trip Miles')
ax1.set_ylabel('Fare ($)')
ax1.set_title(f'Taxi Fare vs Trip Miles ({device_name})')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: MSE over iterations
ax2.plot(range(1, iterations + 1), mse_history, 'b-', linewidth=2, marker='o')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('MSE')
ax2.set_title('MSE Convergence')
ax2.grid(True, alpha=0.3)
ax2.set_yscale('log')

plt.tight_layout()
plt.savefig('taxi_regression_result.png', dpi=150, bbox_inches='tight')
print("\n✓ Plot saved to 'taxi_regression_result.png'")
plt.show()

# Installation guide if using CPU
if GPU_LIBRARY is None or GPU_LIBRARY == "pytorch_cpu":
    print("\n" + "=" * 60)
    print("TO ENABLE GPU ACCELERATION:")
    print("=" * 60)
    print("\nOption 1: PyTorch (RECOMMENDED for Windows)")
    print("  pip install torch --index-url https://download.pytorch.org/whl/cu121")
    print("\nOption 2: CuPy (requires CUDA Toolkit)")
    print("  1. Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads")
    print("  2. pip install cupy-cuda12x")
    print("\nCheck setup with: python check_cuda.py")
    print("=" * 60)