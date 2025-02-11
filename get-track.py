import os
import csv
import re
from glob import glob
import mutagen
import pandas as pd

music_dir = "/Users/willjasen/Library/Mobile Documents/com~apple~CloudDocs/Media/LPC Ultimate Session Bundle/LPC USB/2018 - Longmont Potion Castle - Where In The Hell Is The Lavender House Soundtrack"
srt_files_dir = "/Users/willjasen/Library/Mobile Documents/com~apple~CloudDocs/wallace-thrasher/-converting-/SRT"
output_csv_path = "/Users/willjasen/Library/Mobile Documents/com~apple~CloudDocs/wallace-thrasher/-converting-/track_info.csv"

mp3_files = glob(os.path.join(music_dir, '*.mp3'), recursive=True)

data_list = []

for mp3_file in mp3_files:
    try:
        audiofile = mutagen.File(mp3_file)
        
        if audiofile is not None and 'TIT2' in audiofile.tags:
            track_name = str(audiofile.tags['TIT2'].text[0]).encode('utf-8').decode('utf-8')
            
             # Remove commas and apostrophes from the MP3 filename
            track_name_no_special_chars = re.sub(r"[,'&#()+/]", "", track_name)

            # Try to get the track number from TRCK tag
            try:
                track_number_str = audiofile.tags['TRCK'].text[0].split('/')[0]
                print(f"Track number for {mp3_file}: {track_number_str}")
            except KeyError as e:
                print(f"Error accessing track info for {mp3_file}: {e}")
                track_number_str = ""
        
        else:
            track_name = "Unknown"
            track_number_str = ""
        
        data_list.append({
            'Track Number': track_number_str,
            'Track Name': track_name_no_special_chars
        })
    
    except Exception as e:
        print(f"Error processing file {mp3_file}: {e}")

# Create a DataFrame and write it to a CSV file, skipping empty lines
df = pd.DataFrame(data_list)
if df.empty:
    # Handle the case where no files were processed successfully
    with open(output_csv_path, 'w') as f:
        f.write('')
else:
    df.to_csv(output_csv_path, index=False, sep=';')

print(f"Track info saved to {output_csv_path}")

with open(output_csv_path, 'r') as f:
    reader = csv.DictReader(f, delimiter=';')
    track_numbers = {row['Track Name']: row['Track Number'] for row in reader}

for filename in os.listdir(srt_files_dir):
    if filename.endswith(".srt"):
        srt_filename = os.path.join(srt_files_dir, filename)
        
        with open(srt_filename, 'r') as f:
            lines = f.readlines()
        
        # Extract the track name from the SRT filename
        srt_track_name = os.path.splitext(filename)[0].rsplit('-',1)[0]
        
        if srt_track_name in track_numbers:
            track_number = track_numbers[srt_track_name]
            
            # Get the base and extension of the filename
            base, ext = os.path.splitext(srt_filename)
            mp3_filename = srt_track_name.replace("'", "'").replace(",", ",")  # Replace apostrophes with curly quotes
            new_mp3_filename = re.sub(r"['\,\.,!?;]","", mp3_filename)  # Remove special characters
            
            # Move the SRT file to its new location and rename the MP3 file accordingly
            new_srt_path = os.path.join(os.path.dirname(base), f"{track_number} - {new_mp3_filename}.srt")
            os.rename(srt_filename, new_srt_path)
            
            # Rename the MP3 file using the modified SRT filename
            mp3_file_path = os.path.join(music_dir, f"{track_number} - {mp3_filename}.mp3")
            if os.path.exists(mp3_file_path):
                os.rename(mp3_file_path, new_mp3_filename + '.mp3')
    
    print(f"Renamed: {srt_filename}")