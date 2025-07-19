# CODE STYLE

## Logging Guidelines (2025-06-01 update)

All logging in Python modules MUST be performed via the centralized `GoGoLogger` singleton from `gogo_logger.py`.

### Usage

- Import the logger:
  ```python
  from gogo_logger import GoGoLogger
  logger = GoGoLogger().get_logger()
  ```
- For convenience, you may also use the shorthand methods:
  ```python
  GoGoLogger().info("Something happened!")
  GoGoLogger().error("Something bad happened!")
  ```

### Logger Features

- The logger follows the **singleton** pattern—use `GoGoLogger()` everywhere.
- Multi-thread safe.
- By default:
  - Logs to file named `gadget.log` (level: DEBUG)
  - Logs to stderr (level: WARNING)
- You may toggle file/stderr logging at runtime:
  ```python
  GoGoLogger().log_to_file(True)
  GoGoLogger().log_to_stderr(False)
  ```
- You may set the log file, and get/set log levels separately for file and stderr:
  ```python
  GoGoLogger().set_log_file('my.log')
  GoGoLogger().set_file_level(logging.INFO)
  GoGoLogger().set_stderr_level(logging.ERROR)
  ```

### Good Practices

- Do NOT use Python’s built-in `print()` for warnings, errors, or status. Use the logger.
- Do NOT use the standard library’s `logging.getLogger()` directly—use `GoGoLogger`.
- Log at the appropriate level:
  - `.debug()` for internal details
  - `.info()` for general events
  - `.warning()` for recoverable problems
  - `.error()` for serious issues
  - `.critical()` for fatal errors
- Do NOT keep your own file handles or logging configuration.

### Example

```python
from gogo_logger import GoGoLogger

logger = GoGoLogger().get_logger()

def do_something():
    logger.debug("Starting something")
    try:
        # work
        logger.info("Something completed successfully")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
```

---

## [Previous STYLE RULES continue below...]

(Keep all other project code style rules as before.)