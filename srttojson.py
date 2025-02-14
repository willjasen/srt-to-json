import re
import json
import glob
import os
import pathlib
import yaml
import ruamel.yaml
from sys import argv
from slugify import slugify


def parse_time(time_string):
    hours = int(re.findall(r'(\d+):\d+:\d+,\d+', time_string)[0])
    minutes = int(re.findall(r'\d+:(\d+):\d+,\d+', time_string)[0])
    seconds = int(re.findall(r'\d+:\d+:(\d+),\d+', time_string)[0])
    milliseconds = int(re.findall(r'\d+:\d+:\d+,(\d+)', time_string)[0])

    return (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds


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
    dir_path = '/Users/willjasen/Library/Mobile Documents/com~apple~CloudDocs/wallace-thrasher/-converting-'
    srt_files = glob.glob(os.path.join(dir_path, '**/*.srt'))

    tracks_metadata = []
    tracks_yml_metadata = []

    for srt_filename in srt_files:
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
        
        print("Track %s : %s (slug = %s)" % (track_number, track_title, slugified_filename))
        
        out_base_filename = slugified_filename + '.json'
        metadata_out_filename = 'metadata.json'
        metadata_out_yml_filename = 'metadata.yml'
        srt_out_filename = os.path.join(dir_path + '/JSON', slugified_filename + '.json')
        metadata_out_path = os.path.join(dir_path, metadata_out_filename)
        metadata_out_yml_path = os.path.join(dir_path, metadata_out_yml_filename)
        
        srt = open(srt_filename, 'r', encoding="utf-8").read()
        parsed_srt = parse_srt(srt)
        
        track_metadata = {
            'Track_Title': track_title,
            'Track_Number': track_number,
            'Track_JSONPath': out_base_filename,
            'Track_Slug': slugified_filename,
            'Speakers_Adjusted': 'false',
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

        # Write metadata to separate file with commas between objects
        with open(metadata_out_path, 'w', encoding="utf-8") as f:
            json.dump(tracks_metadata, f, indent=2, separators=(',', ': '))

        # print("YML metadata written to %s" % metadata_out_yml_path)
        with open(metadata_out_yml_path, 'w') as f:
            yaml.dump(tracks_yml_metadata, f, default_flow_style=False)
        
        # Write parsed SRT to main JSON file
        with open(srt_out_filename, 'w', encoding="utf-8") as f:
            json.dump(parsed_srt, f, indent=2)
elif len(argv) == 1:
    print('Type \'srttojson.py\'')
else:
    print('Wrong command.')