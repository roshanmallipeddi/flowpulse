import numpy as np

from src.pipeline.numpy_transforms import (
    normalize,
    z_score,
    bin_values,
    rolling_average,
    detect_outliers,
)


# ----------------------------
# normalize
# ----------------------------

def test_normalize_basic():
    arr = np.array([0.0, 5.0, 10.0])

    result = normalize(arr)

    expected = np.array([0.0, 0.5, 1.0])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected)


def test_normalize_empty():
    arr = np.array([])

    result = normalize(arr)

    assert isinstance(result, np.ndarray)
    assert result.size == 0


def test_normalize_nan():
    arr = np.array([1.0, 2.0, np.nan, 3.0])

    result = normalize(arr)

    expected = np.array([0.0, 0.5, np.nan, 1.0])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected, equal_nan=True)


# ----------------------------
# z_score
# ----------------------------

def test_z_score_basic():
    arr = np.array([1.0, 2.0, 3.0])

    result = z_score(arr)

    expected = np.array([-1.22474487, 0.0, 1.22474487])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected, atol=1e-6)


def test_z_score_empty():
    arr = np.array([])

    result = z_score(arr)

    assert isinstance(result, np.ndarray)
    assert result.size == 0


def test_z_score_nan():
    arr = np.array([1.0, 2.0, np.nan, 3.0])

    result = z_score(arr)

    expected = np.array([-1.22474487, 0.0, np.nan, 1.22474487])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected, atol=1e-6, equal_nan=True)


# ----------------------------
# bin_values
# ----------------------------

def test_bin_values_basic():
    arr = np.array([0.0, 2.0, 4.0, 6.0])

    result = bin_values(arr, n_bins=2)

    expected = np.array([0.0, 0.0, 1.0, 1.0])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected)


def test_bin_values_empty():
    arr = np.array([])

    result = bin_values(arr, n_bins=3)

    assert isinstance(result, np.ndarray)
    assert result.size == 0


def test_bin_values_nan():
    arr = np.array([1.0, np.nan, 3.0, 5.0])

    result = bin_values(arr, n_bins=2)

    expected = np.array([0.0, np.nan, 1.0, 1.0])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected, equal_nan=True)


# ----------------------------
# rolling_average
# ----------------------------

def test_rolling_average_basic():
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    result = rolling_average(arr, window=3)

    expected = np.array([2.0, 3.0, 4.0])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected)


def test_rolling_average_empty():
    arr = np.array([])

    result = rolling_average(arr, window=3)

    assert isinstance(result, np.ndarray)
    assert result.size == 0


def test_rolling_average_nan():
    arr = np.array([1.0, np.nan, 3.0, 5.0])

    result = rolling_average(arr, window=2)

    expected = np.array([1.0, 3.0, 4.0])
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, expected, equal_nan=True)


# ----------------------------
# detect_outliers
# ----------------------------

def test_detect_outliers_iqr_basic():
    arr = np.array([10.0, 12.0, 11.0, 13.0, 100.0])

    result = detect_outliers(arr, method="iqr")

    expected = np.array([False, False, False, False, True])
    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert np.array_equal(result, expected)


def test_detect_outliers_empty():
    arr = np.array([])

    result = detect_outliers(arr, method="iqr")

    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert result.size == 0


def test_detect_outliers_zscore_nan():
    arr = np.array([10.0] * 20 + [np.nan, 1000.0])

    result = detect_outliers(arr, method="zscore")

    expected = np.array([False] * 20 + [False, True])
    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert np.array_equal(result, expected)