import numpy as np


def normalize(array):
    """
    Min-max normalize a numpy array to range [0, 1].

    Rules:
    - Empty array -> empty array
    - All-NaN array -> array of NaN with same shape
    - Constant non-NaN values -> zeros
    - NaN values remain NaN
    """
    array = np.asarray(array, dtype=float)

    if array.size == 0:
        return array.copy()

    if np.isnan(array).all():
        return np.full_like(array, np.nan, dtype=float)

    min_val = np.nanmin(array)
    max_val = np.nanmax(array)

    if max_val == min_val:
        result = np.zeros_like(array, dtype=float)
        result[np.isnan(array)] = np.nan
        return result

    return (array - min_val) / (max_val - min_val)


def z_score(array):
    """
    Standardize array to mean=0 and std=1.

    Rules:
    - Empty array -> empty array
    - All-NaN array -> array of NaN with same shape
    - Zero std -> zeros
    - NaN values remain NaN
    """
    array = np.asarray(array, dtype=float)

    if array.size == 0:
        return array.copy()

    if np.isnan(array).all():
        return np.full_like(array, np.nan, dtype=float)

    mean = np.nanmean(array)
    std = np.nanstd(array)

    if std == 0:
        result = np.zeros_like(array, dtype=float)
        result[np.isnan(array)] = np.nan
        return result

    return (array - mean) / std


def bin_values(array, n_bins):
    """
    Discretize values into n_bins equal-width bins.

    Returns integer bin labels from 0 to n_bins-1 as float array
    so NaN values can be preserved.

    Rules:
    - Empty array -> empty array
    - All-NaN array -> array of NaN with same shape
    - Constant non-NaN values -> zeros
    - NaN values remain NaN
    """
    array = np.asarray(array, dtype=float)

    if array.size == 0:
        return array.copy()

    if n_bins <= 0:
        raise ValueError("n_bins must be greater than 0")

    if np.isnan(array).all():
        return np.full_like(array, np.nan, dtype=float)

    min_val = np.nanmin(array)
    max_val = np.nanmax(array)

    if min_val == max_val:
        result = np.zeros_like(array, dtype=float)
        result[np.isnan(array)] = np.nan
        return result

    bins = np.linspace(min_val, max_val, n_bins + 1)

    result = np.full(array.shape, np.nan, dtype=float)
    valid_mask = ~np.isnan(array)

    labels = np.digitize(array[valid_mask], bins, right=False) - 1
    labels = np.clip(labels, 0, n_bins - 1)

    result[valid_mask] = labels
    return result


def rolling_average(array, window):
    """
    Compute rolling average with configurable window size.

    NaN-aware behavior:
    - For each window, compute mean of non-NaN values
    - If a full window is all NaN, result is NaN

    Rules:
    - Empty array -> empty array
    - window <= 0 or window > len(array) -> empty array
    """
    array = np.asarray(array, dtype=float)

    if array.size == 0:
        return array.copy()

    if window <= 0 or window > array.size:
        return np.array([], dtype=float)

    valid = ~np.isnan(array)
    filled = np.where(valid, array, 0.0)

    value_cumsum = np.cumsum(filled)
    count_cumsum = np.cumsum(valid.astype(int))

    window_sums = value_cumsum[window - 1:].copy()
    window_counts = count_cumsum[window - 1:].copy()

    if window > 1:
        window_sums[1:] = window_sums[1:] - value_cumsum[:-window]
        window_counts[1:] = window_counts[1:] - count_cumsum[:-window]

    result = window_sums / window_counts
    result[window_counts == 0] = np.nan

    return result


def detect_outliers(array, method="iqr"):
    """
    Return boolean mask of outliers.

    Supported methods:
    - 'iqr': 1.5 * IQR rule
    - 'zscore': absolute z-score > 3

    Rules:
    - Empty array -> empty boolean array
    - NaN values are never marked as outliers
    """
    array = np.asarray(array, dtype=float)

    if array.size == 0:
        return np.array([], dtype=bool)

    nan_mask = np.isnan(array)

    if method == "iqr":
        if nan_mask.all():
            return np.zeros(array.shape, dtype=bool)

        q1 = np.nanpercentile(array, 25)
        q3 = np.nanpercentile(array, 75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        result = (array < lower) | (array > upper)
        result[nan_mask] = False
        return result

    if method == "zscore":
        z = z_score(array)
        result = np.abs(z) > 3
        result[nan_mask] = False
        return result

    raise ValueError("method must be 'iqr' or 'zscore'")