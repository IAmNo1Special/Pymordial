# TODOs

## ~~[x] 1. ERROR Handling~~

### <span style="color: red;">~~Issue:~~</span>

~~Add error handling for adb_shell.transport.tcp_connection.ConnectionAbortedError. This error is thrown when the ADB connection is lost.~~

~~Common causes are:~~
~~- BlueStacks closing manually/unexpectedly after ADB connection is already established.~~

### <span style="color: green;">~~Solution:~~</span>

~~- [x] Add error handling for this error and attempt to reconnect. If reconnection fails, quietly exit the program.~~

## ~~[x] 2. Critical Optimization: Streaming Integration~~

### <span style="color: red;">~~Issue:~~</span>
~~Video streaming capability is not fully integrated into the core capture logic. `PymordialController.capture_screen()` always falls back to the slow `screencap` command (~300ms+), even if `start_streaming()` has been called.~~

### <span style="color: green;">~~Solution:~~</span>
~~- [x] Modify `capture_screen` in `PymordialController` to check `self.is_streaming`.~~
~~- [x] If true, retrieve the latest frame from `self.adb.get_latest_frame()`.~~
~~- [x] Handle the format difference: `get_latest_frame` returns `numpy.ndarray`, while `capture_screen` currently returns `bytes`.~~
~~- [x] Update `ImageController` and `TextController` to accept `numpy.ndarray` inputs directly to avoid encoding overhead.~~

## ~~[x] 3. Missing Implementation: `PymordialPixel` Support~~

### <span style="color: red;">~~Issue:~~</span>
~~`is_element_visible` in `PymordialController` raises `NotImplementedError` for `PymordialPixel`, despite `find_element` supporting it.~~

### <span style="color: green;">~~Solution:~~</span>
~~- [x] Add a handler for `PymordialPixel` in `is_element_visible`, delegating to `self.find_element(...) is not None`.~~

## ~~[x] 4. Fragility: BlueStacks Window Handling~~

### <span style="color: red;">~~Issue:~~</span>
~~`capture_loading_screen` in `BluestacksController` uses `win32gui.SetWindowPos` to force the BlueStacks window to the foreground to take a screenshot. This steals focus from the user.~~

### <span style="color: green;">~~Solution:~~</span>
~~- [x] Investigate less intrusive methods for capturing the window content, such as `PrintWindow` API or ADB-based screencaps if ADB is available during loading (though often it is not).~~
~~- [x] Consider making the window title configurable to support multi-instance setups.~~

## 5. Code Consistency & Cleanup

### <span style="color: red;">Issue:</span>
Several minor inconsistencies and potential improvements:
1. `ImageController.where_element` raises `NotImplementedError` for non-`PymordialImage` types but hints `PymordialElement`.
2. `TextController` has duplicated OCR dispatch logic.
3. `AdbController.open_app` uses `CMD_MONKEY` instead of `am start`.
4. `ImageController.where_element` can loop infinitely if `max_tries` is `None`.

### <span style="color: green;">Solution:</span>
- [ ] Narrow type hints or implement support for other elements in `where_element`.
- [ ] Refactor `TextController` OCR dispatch into a helper method.
- [ ] Switch to `am start` for opening apps if appropriate.
- [ ] Ensure infinite retry behavior in `where_element` is intentional or add a safeguard.