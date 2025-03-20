import ctypes
import platform

# Determine the OS and set the shared library path
if platform.system() == "Windows":
    # For Windows, load the .dll file
    v = ctypes.CDLL("Vectorizer\\windows\\vectorizer.dll")
elif platform.system() == "Darwin":
    # For macOS, load the .so file
    v = ctypes.CDLL("Vectorizer/macOS/vectorizer.so")
elif platform.system() == "Linux":
    # For Linux, load the .so file
    v = ctypes.CDLL("Vectorizer/linux/vectorizer.so")
else:
    raise OSError("Unsupported operating system")

# Define the SentimentVector structure
class SentimentVector(ctypes.Structure):
    _fields_ = [("magnitude", ctypes.c_int),
                ("polarity", ctypes.c_int),
                ("intensity", ctypes.c_double)]

# Set return types for functions
v.create.restype = ctypes.POINTER(SentimentVector)
v.s2v.restype = ctypes.POINTER(SentimentVector)
v.v2s.restype = ctypes.c_double
v.combine.restype = ctypes.POINTER(SentimentVector)

# Set argument types for functions
v.create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double]
v.s2v.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_double]
v.v2s.argtypes = [ctypes.POINTER(SentimentVector)]
v.combine.argtypes = [ctypes.POINTER(SentimentVector), ctypes.POINTER(SentimentVector)]

def _create(magnitude, polarity, intensity):
    return v.create(magnitude, polarity, intensity)

def s2v(magnitude, polarity, intensity):
    return _create(magnitude, polarity, intensity)

def v2s(sentiment_vector):
    return v.v2s(sentiment_vector)

def combine(v1, v2):
    return v.combine(v1, v2)