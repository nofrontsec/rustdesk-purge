# RustDesk purge.py

A script to clean up inactive devices from a RustDesk server. Please only execute it with the `delete` command when approaching the device limit (check the current number of registered devices at the bottom of the RustDesk "Devices" menu).

## Usage

The script can be run on the RustDesk server itself and supports two commands: `view` and `delete`.
You can run the script anywhere, as long as you give it the URL to your RustDesk API.

### Viewing Devices (`view`)

This command lists devices that meet specific criteria, such as the number of days they have been offline. It does not perform any modifications and is therefore always "safe to execute." It is useful for checking how many of the registered devices could potentially be deleted.

**Example:**
`python3 purge.py view --url http://127.0.0.1:21114 --offline_days 30`


**Parameters:**
- `--url` (Required): The base URL of the RustDesk API (e.g., `http://127.0.0.1:21114`).
- `--offline_days`: Returns devices that have been offline for longer than the specified number of days (e.g., 30).
- `--id`, `--device_name`, `--user_name`, `--group_name` (Optional): Additional filters to narrow down the device selection.

### Deleting Devices (`delete`)

This command disables and deletes devices that meet the specified criteria.

**Example:**
`python3 purge.py delete --url http://127.0.0.1:21114 --offline_days 30`


**Parameters:**  
Same as the `view` command.

**Process:**
1. The script lists devices that can be deleted.
2. It requests confirmation before proceeding.
3. Upon confirmation, it disables and deletes the devices one by one.
