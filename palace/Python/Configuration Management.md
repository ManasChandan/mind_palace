## 🛠 Configuration Management Patterns

### 1. The Wrapper Class (Mapping Object)

This pattern wraps a raw dictionary to provide a cleaner interface. By using "Magic Methods" like `__getitem__`, we make the object behave like a native dictionary.

* **Best for:** Adding custom logic (like validation or defaults) to raw data.

```python
class Config:
    def __init__(self, data):
        self._data = data
    
    def __getitem__(self, key):
        return self._data[key]

# Usage: config["database"]

```

### 2. The Singleton Pattern

A design pattern that ensures a class has only **one instance** in memory. If you try to create a second `Config()` object, Python simply returns the first one created.

* **Best for:** Heavy operations like Disk I/O or Database connections where you only want to do the work once.

```python
class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

```

### 3. Utility (Static) Classes

Classes that are never turned into objects (`Config()`). They serve as containers for organized constants or "helper" functions.

* **Best for:** Grouping related tools together without needing to maintain "state."

```python
class APIConstants:
    URL = "https://api.myapp.com"
    TIMEOUT = 30
    
# Usage: APIConstants.URL (No object needed)

```

### 4. The Module Pattern (The Pythonic Singleton)

In Python, every `.py` file is a singleton by default. When you import a variable from a file, Python loads it into memory once and shares that same version with every other file that imports it.

* **Best for:** Global configurations and simple, clean code.

```python
# config_manager.py
import tomllib
settings = tomllib.load(open("config.toml", "rb"))

# main.py
from config_manager import settings
print(settings["version"])

```

---

### Comparison Summary

| Pattern | Type | Efficiency | Use Case |
| --- | --- | --- | --- |
| **Wrapper** | Standard Class | Medium | Adding behavior to data. |
| **Singleton** | Special Class | High | Restricting to one instance. |
| **Utility** | Static Class | High | Grouping constants/helpers. |
| **Module** | File-based | Highest | Global app-wide settings. |

---