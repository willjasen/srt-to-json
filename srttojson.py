import re
import json
import os
import pathlib
import yaml
from sys import argv
from slugify import slugify
import pytz
from datetime import datetime, timezone

def convert_to_iso8601(timestamp_str):
    """
    Convert a Unix epoch timestamp string (e.g. "0211182052") to an ISO 8601 date.
    
    Args:
    timestamp_str (str): The input timestamp string.
    
    Returns:
    str: The input timestamp as an ISO 8601 date
    """
    # Remove the leading zeros from the timestamp and convert it to an integer
    timestamp = int(timestamp_str.lstrip('0'))
    
    # Convert the timestamp to a datetime object with Eastern Standard Time timezone
    eastern_standard_time = pytz.timezone('US/Eastern')
    dt = datetime.fromtimestamp(timestamp, eastern_standard_time)
    
    # Return the ISO 8601 date as a string
    return dt.isoformat()

def parse_srt(srt_string):
    srt_list = []
    
    for line in srt_string.split('\n\n'):
        if line != '':
            index = int(re.match(r'\d+', line).group())
            
            pos = re.search(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+',
                            line).end() + 1
            content = line[pos:]
            speaker, text = content.split("|")
            
            start_time = re.findall(
                r'(\d+:\d+:\d+,\d+) --> \d+:\d+:\d+,\d+', line)[0]
            end_time = re.findall(
                r'\d+:\d+:\d+,\d+ --> (\d+:\d+:\d+,\d+)', line)[0]
            
            srt_list.append({
                'Index': index,
                'Start Time': start_time,
                'End Time': end_time,
                'Speaker': speaker,
                'Text': text
            })
    
    return srt_list

if len(argv) == 1:
    dir_path = '/Users/willjasen/Library/Mobile Documents/com~apple~CloudDocs/wallace-thrasher/-to convert subtitles and upload-'
else:
    print('Type \'srttojson.py <directory>\'')
    exit(1)

tracks_metadata = []
tracks_yml_metadata = []

for root, _, files in os.walk(dir_path):
    for file in files:
        if file.endswith('.srt'):
            srt_filename = os.path.join(root, file)
            out_filename = srt_filename.replace('.srt', '.json')
            base_filename = pathlib.Path(srt_filename).stem
            no_trailing_numbers_filename = re.sub(r'-\d+$', '', base_filename)

            # Get the track number from the filename
            parts = no_trailing_numbers_filename.split()
            leading_digits = parts[0]
            try:
                track_number = int(leading_digits.lstrip('0'))
            except ValueError:
                print("Error: could not extract track number from filename %s" % srt_filename)
                continue

            # Get the track title from the filename
            no_leading_numbers_filename = re.sub(r'^\d+ - ', '', no_trailing_numbers_filename)
            track_title = no_leading_numbers_filename
            # Slugify the filename
            slugified_filename = slugify(track_title)
            print("Processing file: %s" % srt_filename)

            out_base_filename = slugified_filename + '.json'
            metadata_out_filename = 'metadata.json'
            metadata_out_yml_filename = 'metadata.yml'
            srt_out_filename = os.path.join(dir_path + '/JSON', slugified_filename + '.json')
            metadata_out_json_path = os.path.join(root + '/..', metadata_out_filename)
            metadata_out_yml_path = os.path.join(root + '/..', metadata_out_yml_filename)
            srt = open(srt_filename, 'r', encoding="utf-8").read()
            parsed_srt = parse_srt(srt)
            unix_utc_timestamp = datetime.now(timezone.utc).timestamp()

            track_metadata = {
                'Last_Modified': int(unix_utc_timestamp),
                'Track_Title': track_title,
                'Track_Number': track_number,
                'Track_JSONPath': out_base_filename,
                'Track_Slug': slugified_filename,
                'Speakers_Adjusted': 'false',
                'Subtitles_Adjusted': 'false',
                'USB_Filename': track_title + '.mp3',
                'Whisper_Model': 'distil-whisper/distil-large-v3'
            }

            tracks_metadata.append(track_metadata)
            tracks_metadata = sorted(tracks_metadata, key=lambda x: x['Track_Number'])

            yml_metadata = {
                'track_title': track_title,
                'track_number': track_number
            }
            tracks_yml_metadata.append(yml_metadata)
            tracks_yml_metadata = sorted(tracks_yml_metadata, key=lambda x: x['track_number'])


            with open(srt_filename, 'r', encoding="utf-8") as f:
                srt_content = f.read()

            parsed_srt = parse_srt(srt_content)

            # Write each track's JSON file
            metadata_out_path = os.path.join(root + '/../JSON', slugified_filename + '.json')
            with open(metadata_out_path, 'w', encoding="utf-8") as f:
                json.dump(parsed_srt, f, indent=2)
            
            # Write metadata.yml
            with open(metadata_out_yml_path, 'w') as f:
                yaml.dump(tracks_yml_metadata, f, default_flow_style=False)
            # Write metadata.json
            with open(metadata_out_json_path, 'w', encoding="utf-8") as f:
                json.dump(tracks_metadata, f, indent=2)

print("Processing complete.")