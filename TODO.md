# TODOs

## 1. ERROR Handling

### <span style="color: red;">Issue:</span>

Add error handling for adb_shell.transport.tcp_connection.ConnectionAbortedError. This error is thrown when the ADB connection is lost.

Common causes are:
- *BlueStacks closing manually/unexpectedly after ADB connection is already established.*

### <span style="color: green;">Solution:</span>

- Add error handling for this error and attempt to reconnect. If reconnection fails, quietly exit the program.