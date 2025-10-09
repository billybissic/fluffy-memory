import os
import re
import difflib
from collections import defaultdict
import json

path = 'W:\Movies'
media_data = {}


def find_fuzzy_duplicates(media_dict, base_path=path, title_threshold=0.8):
    matches = defaultdict(list)
    items = list(media_dict.items())

    for i, (key1, data1) in enumerate(items):
        title1 = data1['cleaned_name']
        year1 = data1['year']

        for j in range(i + 1, len(items)):
            key2, data2 = items[j]
            title2 = data2['cleaned_name']
            year2 = data2['year']

            if year1 and year1 == year2:
                ratio = difflib.SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
                if ratio >= title_threshold:
                    match_key = f"{title1} ({year1})"
                    full_path_1 = os.path.join(base_path, key1)
                    full_path_2 = os.path.join(base_path, key2)
                    matches[match_key].extend([full_path_1, full_path_2])

    # Deduplicate file paths
    for k in matches:
        matches[k] = sorted(set(matches[k]))

    # Optional: print results
    for match_key, files in matches.items():
        if len(files) > 1:
            print(f"\nDuplicate: {match_key}")
            for f in files:
                print(f"  - {f}")

    return matches

def find_year(text):
    """Returns a list of 4-digit numbers (likely years) found in the input string."""
    #year = re.findall(r'\b\d{4}\b', text)

    year = re.findall(r'\b(?:19|20)\d{2}\b', text)
    match = year[0] if year else None  # Safely return the first match
    #print(f"Year: {match}")
    return match


def to_uppercase(text):
    result = text.upper()
    #print(f"Uppercased: {result}")
    return result


def extract_title(text):
    # Replace periods with spaces
    cleaned = text.replace('.', ' ')

    # Lowercase for uniform filtering
    cleaned = cleaned.lower()

    # Remove common quality and encoding tags
    cleaned = re.sub(r'\b(Aac|2 0|5 1|Dd5|Tigole|-Nogrp|-Smurf|10Bit|360P|480P|720p|1080p|2160p|480p|H 264|x264|x265|h264|h265|hdr|bluray|webrip|dvdrip|brrip|web-dl|webdl|Rarbg|-Rarbg)\b', '',
                     cleaned)

    # Remove year (optional – comment out if you want to keep it)
    cleaned = re.sub(r'\b(19|20)\d{2}\b', '', cleaned)

    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())

    # Title-case the result (optional)
    title = cleaned.title()

    # print(f"Title: {title}")
    return title


def remove_after(text, substring):
    index = text.find(substring)
    if index != -1:
        result = text[:index].rstrip('. ')
        #print(f"{result}")
        return result
    # print(f"{substring}")
    return text


def remove_suffix_and_after(text, suffix, tolerance=5):
    index = text.rfind(suffix)
    if index != -1 and index + len(suffix) >= len(text) - tolerance:
        result = text[:index].rstrip('. ')
        #print(f"Removing suffix '{suffix}' and everything after: '{result}'")
        return result
    #print(f"Suffix '{suffix}' not found within {tolerance} characters of the end. Returning original text.")
    return text


def remove_exact_string(text, target):
    result = text.replace(target, '')
    #print(f"Removed '{target}': '{result}'")
    return result


def remove_release_groups(text):
    release_groups = ['7SINS', 'AMRAP', 'WEB -AMRAP', 'AMZN WEB', 'AMZN', 'BVS', 'DON', 'DIMEPIECE', 'ULYSSE', 'JAPHSON', 'DIMEPIECE', 'DSNP', 'DRONES', 'LAMA', 'KOGI', 'MVD', 'OFT', 'THR', 'VXT', 'NF', 'NIKT0', 'PROPER', '-ELEVATE', 'SPHD', 'XOR', 'X0R', 'USURY', 'YIFY']
    for group in release_groups:
        text = remove_exact_string(text, group)
    return text


def remove_char_if_at_end(text, char):
    if text.endswith(char):
        result = text[:-1]
        #print(f"Removed '{char}' at end: '{result}'")
        return result
    #print(f"'{char}' not at end. No change: '{text}'")
    return text


def trim_string(text, chars=None):
    """
    Trims specified characters from both ends of the string.
    If no chars are provided, it trims whitespace.
    """
    result = text.strip(chars) if chars else text.strip()
    #print(f"Trimmed string: '{result}'")
    return result


'''def find_fuzzy_duplicates(media_dict, title_threshold=0.8):
    matches = defaultdict(list)
    checked = set()
    items = list(media_dict.items())

    for i, (key1, data1) in enumerate(items):
        title1 = data1['cleaned_name']
        year1 = data1['year']

        for j in range(i + 1, len(items)):
            key2, data2 = items[j]
            title2 = data2['cleaned_name']
            year2 = data2['year']

            if year1 and year1 == year2:
                # Compare title similarity
                ratio = difflib.SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
                if ratio >= title_threshold:
                    match_key = f"{title1} ({year1})"
                    matches[match_key].extend([key1, key2])

        checked.add(key1)

    # Remove duplicates
    for k in matches:
        matches[k] = list(set(matches[k]))

    # Display results
    for match_key, files in matches.items():
        if len(files) > 1:
            print(f"\nPossible duplicate: {match_key}")
            for f in files:
                print(f"  - {f}")

    return matches
'''


def write_duplicates_to_json(duplicates, filename="duplicates.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Duplicate data written to '{filename}'")


# List all directories in the given path
dir_names = [name for name in os.listdir(path)
             if os.path.isdir(os.path.join(path, name))]
#print(dir_names)
for dirname in dir_names:
    title = extract_title(dirname)
    title = to_uppercase(title)
    title = remove_release_groups(title)
    title = remove_after(title, 'RARBG')
    title = remove_after(title, 'AAC')
    title = remove_after(title, 'AC3')
    title = remove_after(title, 'AVC')
    title = remove_after(title, 'BDRIP')
    title = remove_after(title, 'BRIP')
    title = remove_after(title, 'BDR9P')
    title = remove_after(title, 'H 264')
    title = remove_after(title, 'DTS')
    title = remove_after(title, 'DD5')
    title = remove_after(title, 'HDR10')
    title = remove_after(title, 'HEVC')
    title = remove_after(title, 'Eac3')
    title = remove_after(title, '270P')
    title = remove_after(title, '360P')
    title = remove_after(title, '480P')
    title = remove_after(title, '720P')
    title = remove_after(title, '800P')
    title = remove_after(title, '1036P')
    title = remove_after(title, '1040P')
    title = remove_after(title, '1080P')
    title = remove_after(title, '1078P')
    title = remove_after(title, '1GB')
    title = remove_after(title, '4K WEB')
    title = remove_after(title, 'XVID')
    title = remove_after(title, '10BIT')
    title = remove_after(title, 'DDP')
    title = remove_after(title, 'DD2')
    title = remove_suffix_and_after(title, '()')
    title = remove_suffix_and_after(title, '(')
    title = remove_exact_string(title, '[]')
    title = remove_suffix_and_after(title, '()')
    title = remove_char_if_at_end(title, '(')
    title = trim_string(title)
    title = remove_char_if_at_end(title, '-')
    #print(f"Original: {dirname}")
    #print(f"Title: {title}")
    year = find_year(dirname)
    media_data[dirname] = {
        "cleaned_name": title,
        "year": year
    }

duplicates = find_fuzzy_duplicates(media_data)
#write_duplicates_to_json(duplicates)

