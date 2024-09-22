#!/usr/bin/env python3

import configparser
import datetime
from datetime import timedelta
import pytz
import sys
import os
import logging
import urllib.parse

try:
    import caldav
except ImportError:
    print("Please install the caldav module using 'pip install caldav'")
    sys.exit(1)

try:
    from icalendar import Calendar, Event
except ImportError:
    print("Please install the icalendar module using 'pip install icalendar'")
    sys.exit(1)

# Optional modules for remote upload
try:
    import ftplib
except ImportError:
    print("Warning: ftplib module not found. FTP upload will not be available.")

try:
    import paramiko
except ImportError:
    print("Warning: paramiko module not found. SFTP/SCP upload will not be available.")


def upload_via_ftp(config, local_file, filename):
    ftp_host = config.get('ftp_host')
    ftp_port = config.getint('ftp_port', 21)
    ftp_username = config.get('ftp_username')
    ftp_password = config.get('ftp_password')
    remote_path = config.get('remote_path', '/')

    try:
        with ftplib.FTP() as ftp:
            ftp.connect(ftp_host, ftp_port)
            ftp.login(ftp_username, ftp_password)

            # Construct the remote file path
            remote_file = os.path.join(remote_path, filename)

            with open(local_file, 'rb') as f:
                ftp.storbinary(f'STOR {remote_file}', f)
        logging.info("File uploaded via FTP successfully.")
    except Exception as e:
        logging.error(f"FTP upload failed: {e}")


def upload_via_sftp(config, local_file, filename):
    sftp_host = config.get('sftp_host')
    sftp_port = config.getint('sftp_port', 22)
    sftp_username = config.get('sftp_username')
    sftp_password = config.get('sftp_password', None)
    sftp_private_key = config.get('sftp_private_key', None)
    sftp_private_key_pass = config.get('sftp_private_key_pass', None)
    remote_path = config.get('remote_path', '/')

    try:
        transport = paramiko.Transport((sftp_host, sftp_port))
        if sftp_private_key:
            private_key = paramiko.RSAKey.from_private_key_file(sftp_private_key, password=sftp_private_key_pass)
            transport.connect(username=sftp_username, pkey=private_key)
        else:
            transport.connect(username=sftp_username, password=sftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Construct the remote file path
        remote_file = os.path.join(remote_path, filename)

        sftp.put(local_file, remote_file)
        sftp.close()
        transport.close()
        logging.info("File uploaded via SFTP/SCP successfully.")
    except Exception as e:
        logging.error(f"SFTP/SCP upload failed: {e}")


def main():
    # Read config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Get general settings
    output_dir = config['DEFAULT'].get('output_dir', '.')
    output_filename = config['DEFAULT'].get('output_filename', 'busy.ics')
    output_file = os.path.join(output_dir, output_filename)
    starthours = int(config['DEFAULT'].get('starthours', '0'))
    endhours = int(config['DEFAULT'].get('endhours', '1440'))  # default to 2 months
    summary_text = config['DEFAULT'].get('summary_text', 'Busy')
    upload_method = config['DEFAULT'].get('upload_method', '').lower()
    log_level = config['DEFAULT'].get('log_level', 'WARNING').upper()

    # Set up logging
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        print(f'Invalid log level: {log_level}')
        numeric_level = logging.WARNING
    logging.basicConfig(level=numeric_level, format='%(levelname)s: %(message)s')

    logging.debug("Script started.")
    logging.debug(f"Output directory: {output_dir}")
    logging.debug(f"Output filename: {output_filename}")
    logging.debug(f"Output file path: {output_file}")
    logging.debug(f"Start hours: {starthours}, End hours: {endhours}")

    # Calculate the time range
    timezone = pytz.utc
    start_time = datetime.datetime.now(timezone) + timedelta(hours=starthours)
    end_time = datetime.datetime.now(timezone) + timedelta(hours=endhours)

    # Initialize a new calendar
    busy_calendar = Calendar()
    busy_calendar.add('prodid', '-//Busy Calendar//mxm.dk//')
    busy_calendar.add('version', '2.0')

    # Loop over resources
    for section in config.sections():
        if section.startswith('RESOURCE'):
            resource_config = config[section]
            url = resource_config.get('url')
            username = resource_config.get('username')
            password = resource_config.get('password')

            if not url or not username or not password:
                logging.error(f"Missing information in section {section}")
                continue

            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.scheme != 'https' and numeric_level <= logging.INFO:
                logging.warning(f"Unencrypted connection to iCal server: {url}")

            # Connect to CalDAV server
            try:
                client = caldav.DAVClient(url, username=username, password=password)
                principal = client.principal()
                calendars = principal.calendars()
                logging.info(f"Connected to {url} successfully.")

                # List available calendars
                for calendar in calendars:
                    cal_name = calendar.name
                    cal_url = calendar.url
                    logging.info(f"Available calendar: {cal_name} - {cal_url}")

                for calendar in calendars:
                    # Get events in the time range
                    results = calendar.date_search(start=start_time, end=end_time)

                    for event in results:
                        try:
                            ical = Calendar.from_ical(event.data)
                            for component in ical.walk():
                                if component.name == "VEVENT":
                                    event_start = component.get('dtstart').dt
                                    event_end = component.get('dtend').dt
                                    event_status = component.get('transp', 'OPAQUE')

                                    # Check if event is busy
                                    if event_status == 'OPAQUE':
                                        # Create a new event with minimal information
                                        busy_event = Event()
                                        busy_event.add('dtstart', event_start)
                                        busy_event.add('dtend', event_end)
                                        busy_event.add('summary', summary_text)
                                        busy_calendar.add_component(busy_event)
                        except Exception as e:
                            logging.error(f"Error processing event: {e}")
                logging.debug(f"Finished processing calendars for {url}")
            except Exception as e:
                logging.error(f"Error connecting to {url}: {e}")
                continue

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write the busy calendar to file
    try:
        with open(output_file, 'wb') as f:
            f.write(busy_calendar.to_ical())
        logging.info(f"Busy ICS file generated at {output_file}")
    except Exception as e:
        logging.critical(f"Failed to write ICS file: {e}")
        sys.exit(1)

    # Check for unencrypted upload methods
    if upload_method == 'ftp' and numeric_level <= logging.INFO:
        logging.warning("FTP is unencrypted. Consider using SFTP/SCP for secure file transfer.")

    # Upload the file if configured
    if upload_method == 'ftp':
        if 'FTP' in config:
            upload_via_ftp(config['FTP'], output_file, output_filename)
        else:
            logging.error("FTP upload settings not found in config.")
    elif upload_method == 'sftp' or upload_method == 'scp':
        if 'SFTP' in config:
            upload_via_sftp(config['SFTP'], output_file, output_filename)
        else:
            logging.error("SFTP/SCP upload settings not found in config.")
    elif upload_method == '':
        logging.info("No upload method specified.")
    else:
        logging.error(f"Unknown upload method '{upload_method}' specified.")

    logging.debug("Script finished.")


if __name__ == "__main__":
    main()