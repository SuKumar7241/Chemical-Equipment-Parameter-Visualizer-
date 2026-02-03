import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend first
import matplotlib.pyplot as plt
import numpy as np

# Create simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.title('Matplotlib Test - Sin Wave')
plt.xlabel('X values')
plt.ylabel('Y values')
plt.legend()
plt.grid(True)

# Save to file instead of showing
plt.savefig('desktop_app/test_plot.png', dpi=150, bbox_inches='tight')
print("Plot saved to desktop_app/test_plot.png")
print("Matplotlib is working correctly!")

# Now test Qt5Agg backend
print("\nTesting Qt5Agg backend...")
try:
    matplotlib.use('Qt5Agg')
    print("Qt5Agg backend set successfully")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    print("FigureCanvasQTAgg imported successfully")
    print("Qt5Agg backend is working!")
except Exception as e:
    print(f"Qt5Agg backend error: {e}")