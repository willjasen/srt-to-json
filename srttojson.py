import re
import json
import glob
import os
import pathlib
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
    dir_path = '/Users/willjasen/Library/Mobile Documents/com~apple~CloudDocs/wallace-thrasher/-testing-'
    srt_files = glob.glob(os.path.join(dir_path, '**/*.srt'))

    for srt_filename in srt_files:
        out_filename = srt_filename.replace('.srt', '.json')

        # slugify the filename
        base_filename = pathlib.Path(srt_filename).stem
        no_trailing_numbers_filename = re.sub(r'-\d+$', '', base_filename)

        parts = no_trailing_numbers_filename.split()
        leading_digits = parts[0]
        track_number = int(leading_digits.lstrip('0'))

        no_leading_numbers_filename = re.sub(r'^\d+-', '', no_trailing_numbers_filename)
        
        slugified_filename = slugify(no_leading_numbers_filename)
        print(track_number)
        print(slugified_filename)
        
        out_filename = os.path.join(dir_path + '/JSON', slugified_filename + '.json')
        srt = open(srt_filename, 'r', encoding="utf-8").read()
        parsed_srt = parse_srt(srt)
        open(out_filename, 'w', encoding="utf-8").write(
            json.dumps(parsed_srt, indent=2, sort_keys=False))
elif len(argv) == 1:
    print('Type \'srttojson.py\'')
else:
    print('Wrong command.')
