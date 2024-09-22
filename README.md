# BusyICS Calendar Generator

## Overview

The BusyICS Calendar Generator is a Python script that connects to one or multiple iCal (CalDAV) servers, retrieves events within a specified time range, and generates an anonymized `.ics` file containing only the busy times. This allows you to share your availability without exposing personal details about your events.

Additionally, the script can automatically upload the generated `.ics` file to a remote web server via FTP, SFTP, SCP, or SSH, as configured. The script includes configurable logging to help you monitor its operation.

## Features

- Connects to multiple iCal servers as specified in a configuration file.
- Retrieves events within a defined time range.
- Identifies busy events and creates a new calendar file with only the busy times.
- Anonymizes event details; the generated `.ics` file contains no personal information.
- Configurable summary text for busy events.
- Automatic upload to a remote server via FTP, SFTP, SCP, or SSH.
- Supports both password and public key authentication for SFTP/SCP.
- Configurable logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- Logs available calendars after authentication.
- Warns when using unencrypted connections.
- Easy setup via a `config.ini` file.

## Prerequisites

- Python 3.x
- Modules:
  - `caldav`
  - `icalendar`
  - `pytz`
  - For FTP upload: `ftplib` (included in the Python standard library)
  - For SFTP/SCP upload: `paramiko`

## Installation

### Setting Up a Python Virtual Environment

It is recommended to use a Python virtual environment to manage dependencies for this script.

1. **Install `virtualenv` if you haven't already:**

   ```bash
   python3 -m pip install virtualenv
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m virtualenv venv
   ```

3. **Activate the virtual environment:**

   On Linux/macOS:

   ```bash
   source venv/bin/activate
   ```

   On Windows:

   ```cmd
   venv\Scripts\activate
   ```

4. **Install the required Python modules:**

   ```bash
   pip install caldav icalendar pytz paramiko
   ```

### Downloading the Script

1. **Clone the repository or download the script:**

   ```bash
   git clone https://github.com/yourusername/busyics-calendar-generator.git
   ```

2. **Navigate to the directory:**

   ```bash
   cd busyics-calendar-generator
   ```

## Configuration

1. **Create the configuration file:**

   Copy the `config.ini.default` file to `config.ini`.

   ```bash
   cp config.ini.default config.ini
   ```

2. **Edit the `config.ini` file:**

   Open `config.ini` in a text editor and configure the following:

   - **General Settings (DEFAULT section):**

     ```ini
     [DEFAULT]
     # Directory where the busy.ics file will be saved
     output_dir = /path/to/output/directory

     # Filename for the busy.ics file
     output_filename = busy.ics

     # Start and end hours from now
     starthours = 0
     endhours = 1440  # Default is 2 months

     # Summary text to use for busy events
     summary_text = Busy

     # Upload method: '', 'ftp', 'sftp', or 'scp'
     upload_method = 

     # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
     log_level = WARNING
     ```

     - `output_dir`: The directory where the generated `.ics` file will be saved.
     - `output_filename`: The filename for the generated `.ics` file.
     - `starthours`: Number of hours from the current time to start collecting events.
     - `endhours`: Number of hours from the current time to stop collecting events.
     - `summary_text`: The text to display for each busy event in the generated file.
     - `upload_method`: Choose the method for uploading the `.ics` file. Options are:
       - `''` (empty string): Do not upload.
       - `'ftp'`: Upload via FTP.
       - `'sftp'` or `'scp'`: Upload via SFTP/SCP/SSH.
     - `log_level`: Set the logging level. Options are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

   - **iCal Resources:**

     For each iCal server you want to connect to, add a new section with the following details:

     ```ini
     [RESOURCE1]
     url = https://example.com/caldav/
     username = your_username
     password = your_password
     ```

     **Example with multiple resources:**

     ```ini
     [RESOURCE1]
     url = https://calendar.example.com/caldav/user1/
     username = user1
     password = password1

     [RESOURCE2]
     url = https://calendar.example.com/caldav/user2/
     username = user2
     password = password2
     ```

   - **FTP Upload Settings:**

     If you set `upload_method = ftp`, configure the FTP settings:

     ```ini
     [FTP]
     ftp_host = ftp.example.com
     ftp_port = 21
     ftp_username = your_ftp_username
     ftp_password = your_ftp_password
     remote_path = /path/on/server/
     ```

     - `ftp_host`: The FTP server address.
     - `ftp_port`: The FTP server port (default is 21).
     - `ftp_username`: Your FTP username.
     - `ftp_password`: Your FTP password.
     - `remote_path`: The path on the server where the file should be uploaded.

   - **SFTP/SCP Upload Settings:**

     If you set `upload_method = sftp` or `upload_method = scp`, configure the SFTP/SCP settings:

     ```ini
     [SFTP]
     sftp_host = sftp.example.com
     sftp_port = 22
     sftp_username = your_sftp_username

     # For password authentication:
     sftp_password = your_sftp_password

     # For key authentication:
     sftp_private_key = /path/to/private/key
     sftp_private_key_pass = private_key_passphrase  ; if your key has a passphrase

     remote_path = /path/on/server/
     ```

     - `sftp_host`: The SFTP/SCP server address.
     - `sftp_port`: The SFTP/SCP server port (default is 22).
     - `sftp_username`: Your SFTP/SCP username.
     - **Authentication Options:**
       - **Password Authentication:**
         - `sftp_password`: Your SFTP/SCP password.
       - **Public Key Authentication:**
         - `sftp_private_key`: The path to your private key file.
         - `sftp_private_key_pass`: The passphrase for your private key, if it is encrypted.
     - `remote_path`: The path on the server where the file should be uploaded.

   - **Instructions on Setting Up a Python Virtual Environment:**

     ```ini
     [VIRTUALENV]
     ; To set up a Python virtual environment for this script, follow these steps:
     ; 1. Install virtualenv if you haven't already:
     ;    python3 -m pip install virtualenv
     ; 2. Create a virtual environment:
     ;    python3 -m virtualenv venv
     ; 3. Activate the virtual environment:
     ;    source venv/bin/activate
     ; 4. Install the required packages:
     ;    pip install caldav icalendar pytz paramiko
     ; 5. Run the script within the virtual environment.
     ```

## Usage

1. **Activate the virtual environment (if not already active):**

   On Linux/macOS:

   ```bash
   source venv/bin/activate
   ```

   On Windows:

   ```cmd
   venv\Scripts\activate
   ```

2. **Run the script:**

   ```bash
   python main.py
   ```

   The script will:

   - Read the configuration from `config.ini`.
   - Connect to each specified iCal server.
   - Retrieve events within the specified time range.
   - Identify busy events.
   - Generate an anonymized `.ics` file at the location specified by `output_dir` and `output_filename`.
   - Upload the `.ics` file to the remote server if configured.
   - Log information based on the configured `log_level`.

3. **Verify the output:**

   - The generated `.ics` file will contain events with:
     - The start and end times of your busy periods.
     - The summary text as specified in `summary_text` (default is "Busy").
   - If upload is configured, verify that the file has been uploaded to the remote server.
   - Review the log output for information about the script's operation.

4. **Import or share the `.ics` file:**

   - You can now import the generated `busy.ics` file into your calendar application or share it with others to inform them of your availability.

## Logging

- **Logging Levels:**

  - `DEBUG`: Detailed information, typically of interest only when diagnosing problems.
  - `INFO`: Confirmation that things are working as expected.
  - `WARNING`: An indication that something unexpected happened, or indicative of some problem in the near future.
  - `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
  - `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running.

- **Configuring Logging Level:**

  Set the `log_level` in the `config.ini` file under the `[DEFAULT]` section.

  ```ini
  log_level = INFO
  ```

- **Logging Features:**

  - After connecting and authenticating to an iCal server, the script logs a list of available calendars with their names and URLs.
  - If the iCal server URL is not using HTTPS and the logging level is `INFO` or `DEBUG`, the script logs a warning about unencrypted connections.
  - If using FTP for uploading and the logging level is `INFO` or `DEBUG`, the script logs a warning about unencrypted file transfer.
  - Errors and exceptions are logged appropriately.
  - All logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) are implemented.

## Example

Assuming your `config.ini` is set up as follows:

```ini
[DEFAULT]
output_dir = /home/user/output
output_filename = busy.ics
starthours = 0
endhours = 1440
summary_text = Busy
upload_method = scp
log_level = INFO

[RESOURCE1]
url = https://calendar.work.com/caldav/
username = work_user
password = work_password

[RESOURCE2]
url = https://calendar.personal.com/caldav/
username = personal_user
password = personal_password

[SFTP]
sftp_host = sftp.example.com
sftp_port = 22
sftp_username = sftp_user
sftp_private_key = /home/user/.ssh/id_rsa
sftp_private_key_pass = your_passphrase
remote_path = /var/www/html/calendar/
```

Running the script will:

- Connect to both your work and personal calendars.
- Collect all events from now until 60 days (approximately 1440 hours).
- Identify all busy periods.
- Generate `/home/user/output/busy.ics` containing only the busy times with the summary "Busy".
- Upload the `busy.ics` file to the remote server via SCP/SFTP at `/var/www/html/calendar/` using public key authentication.
- Log the available calendars after authentication.
- Warn if any connections are unencrypted.
- Use the configured logging level to display information.

## Troubleshooting

- **Module Not Found Errors:**

  If you encounter errors about missing modules, ensure all required modules are installed:

  ```bash
  pip install caldav icalendar pytz paramiko
  ```

- **Connection Errors:**

  - Verify the `url`, `username`, and `password` in your `config.ini`.
  - Ensure you have network connectivity to the iCal and remote servers.
  - Check firewall settings that may block FTP, SFTP, or SCP connections.

- **Permissions Errors:**

  - Ensure you have write permissions to the directory specified in `output_dir`.
  - Verify that the remote server allows write access to the specified `remote_path`.

- **Upload Failures:**

  - Ensure that the FTP or SFTP/SCP credentials are correct.
  - Check if the remote path exists and is writable.
  - Review any error messages printed by the script for clues.

- **Logging Issues:**

  - If the script is not logging as expected, check the `log_level` setting in `config.ini`.
  - Ensure that the logging level is set to the desired level (`DEBUG`, `INFO`, etc.).

## Security Considerations

- **Credentials:**

  - Store the `config.ini` file securely, as it contains your usernames and passwords.
  - Consider restricting file permissions to prevent unauthorized access:

    ```bash
    chmod 600 config.ini
    ```

  - Avoid sharing the `config.ini` file.

- **Data Privacy:**

  - The generated `.ics` file contains only the start and end times of your busy periods and a generic summary.
  - No personal details or event descriptions are included.

- **Encrypted Connections:**

  - FTP is not encrypted; consider using SFTP/SCP for secure file transfers.
  - Ensure that your CalDAV servers support HTTPS for encrypted calendar data retrieval.
  - The script will warn you if unencrypted connections are used when logging level is set to `INFO` or `DEBUG`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes or improvements.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [caldav](https://github.com/python-caldav/caldav) - A CalDAV client library for Python.
- [icalendar](https://icalendar.readthedocs.io/en/latest/) - A parser/generator of iCalendar files for Python.
- [paramiko](https://www.paramiko.org/) - A Python implementation of SSHv2 for SFTP and SSH functionality.