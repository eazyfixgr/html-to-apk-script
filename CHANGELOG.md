# Changelog

All notable changes to the HTML to APK Converter project.

## [2.0.0] - 2024

### Security Fixes

#### Critical
- **Fixed command injection vulnerability** (`html_to_apk_converter.py:1576-1654`)
  - Added `safe_run_command()` method that uses list-based command execution
  - Disabled `shell=True` by default (except Windows where required)
  - Commands are split safely to prevent injection attacks
  - Previous: `subprocess.run(command, shell=True)` with user-controlled strings
  - Now: `subprocess.run(cmd_list, shell=False)` with validated input

#### High
- **App ID validation** (`html_to_apk_converter.py:1048-1052`)
  - Added `validate_app_id()` method with regex validation
  - Enforces reverse domain notation (e.g., `com.example.app`)
  - Pattern: `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$`
  - Prevents malformed IDs that could cause build failures or security issues

- **App name sanitization** (`html_to_apk_converter.py:1054-1059`)
  - Added `sanitize_app_name()` method
  - Removes special characters that could break builds
  - Prompts user when modifications are needed
  - Keeps only alphanumeric, spaces, hyphens, and underscores

- **Input validation** (`html_to_apk_converter.py:1076-1128`)
  - Enhanced `validate_input()` with comprehensive checks
  - Validates paths exist and are accessible
  - Checks for required files before starting build
  - Provides clear error messages for each validation failure

### Bug Fixes

#### Critical
- **Fixed PIL image preview crash** (`html_to_apk_converter.py:751-817`)
  - Removed broken `pil_to_base64()` method
  - Now uses `ImageTk.PhotoImage()` directly
  - Added proper import of `ImageTk` module
  - Fixed memory leaks by properly managing image references
  - Added None checks to prevent crashes on image cleanup

#### High
- **Improved process cleanup** (`html_to_apk_converter.py:1656-1749`)
  - Added `finally` block to `run_command_with_timeout()`
  - Ensures processes are terminated even on exceptions
  - Uses graceful terminate() followed by kill() if needed
  - Prevents zombie processes and resource leaks

- **Fixed configuration corruption** (`html_to_apk_converter.py:290-322`)
  - Atomic write using temporary file + rename
  - Prevents corruption if program crashes during save
  - Added UTF-8 encoding for international characters
  - Corrupted configs are automatically backed up to `.bak` file

#### Medium
- **HTML directory validation** (`html_to_apk_converter.py:1061-1074`)
  - Added `validate_html_directory()` method
  - Pre-flight check for `index.html` before starting build
  - Validates directory exists and is accessible
  - Provides specific error messages for each failure case

- **Better file copy error handling** (`html_to_apk_converter.py:2015-2073`)
  - Individual file copy errors don't stop entire process
  - Permission errors are logged but don't fail build
  - Counts files and directories successfully copied
  - Verifies `index.html` exists after copy

### Improvements

#### Code Quality
- **Removed duplicate imports** (`html_to_apk_converter.py:751-817`)
  - Removed redundant `import tkinter as tk` in `update_icon_preview()`
  - Removed redundant `import tkinter as tk` in `update_splash_preview()`
  - Import is already at module level

- **Consistent path handling**
  - All paths use `pathlib.Path` objects
  - Added `.resolve()` calls for absolute paths
  - Cross-platform compatibility improved

- **Better error messages**
  - Added context to all error messages
  - Included specific details (return codes, file names)
  - Limited log output to prevent flooding (10 lines max)
  - Added file/directory counts for user feedback

#### Error Handling
- **Granular configuration loading** (`html_to_apk_converter.py:196-288`)
  - Each setting loads independently
  - Single setting error doesn't break entire config
  - Each setting wrapped in try-except
  - Failed settings use default values

- **Resource management**
  - Added proper cleanup in all subprocess operations
  - Timeout handling for hanging processes
  - Graceful degradation when components unavailable

#### User Experience
- **File renamed**
  - `html_to_apk icon ok plugins v1.py` → `html_to_apk_converter.py`
  - Removed spaces for easier command-line usage
  - More professional naming convention

- **Better validation feedback**
  - App ID validation shows format rules
  - App name sanitization prompts for approval
  - HTML directory errors are specific
  - Image size validation with recommendations

- **Improved cancellation**
  - Checks `is_building` flag during file operations
  - Clean process termination on cancel
  - Proper cleanup even when cancelled
  - User feedback on cancellation

### Performance

- **Reduced log output**
  - Limited error/output lines to 10 per command
  - Prevents UI freeze with large outputs
  - Still captures all logs, just limits display

- **Progress tracking**
  - More granular progress updates
  - File/directory count reporting
  - Better time estimates

### Documentation

- **Added README.md**
  - Comprehensive usage guide
  - Installation instructions
  - Troubleshooting section
  - Plugin documentation
  - App ID format specification

- **Added CHANGELOG.md**
  - Detailed change log
  - Security fix documentation
  - Bug fix details with line numbers
  - Improvement tracking

### Testing Recommendations

For developers reviewing these changes:

1. **Test command injection fix**:
   - Try app names with special characters: `"; rm -rf /`
   - Try app IDs with shell metacharacters: `com.test$(whoami).app`
   - Verify commands are split safely

2. **Test PIL image preview**:
   - Select various image formats (PNG, JPG, etc.)
   - Select very large images (>10MB)
   - Test with corrupted image files

3. **Test configuration handling**:
   - Corrupt config file manually
   - Verify backup is created
   - Check UTF-8 characters in paths

4. **Test validation**:
   - Use invalid app IDs (single segment, uppercase, special chars)
   - Use app names with emoji/special characters
   - Select HTML directories without index.html

5. **Test cancellation**:
   - Start build and cancel immediately
   - Cancel during file copy
   - Cancel during plugin installation
   - Verify no zombie processes

### Migration Notes

No breaking changes for end users. All existing configuration files will continue to work.

### Known Issues

None at this time.

### Contributors

- Code improvements and security fixes
- Documentation and testing

---

## [1.0.0] - Original Release

Initial release with basic functionality:
- HTML to APK conversion
- Plugin selection
- Icon and splash screen generation
- Configuration persistence
