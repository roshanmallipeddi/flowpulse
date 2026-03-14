import numpy as np
import time
from src.pipeline.numpy_transforms import detect_outliers

data = np.random.randn(1_000_000)

start = time.time()
iqr = detect_outliers(data, method="iqr")
print("IQR time:", time.time() - start)

start = time.time()
z = detect_outliers(data, method="zscore")
print("Z-score time:", time.time() - start)

print("IQR outliers:", iqr.sum())
print("Z-score outliers:", z.sum())
print("Same outliers?", np.array_equal(iqr, z))