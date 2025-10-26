import os
import re
import difflib
from collections import defaultdict
import json

path = 'Z:/Movies'
media_dir_dict = {}
media_file_dict = {}


EXTENSION_GROUPS = {
    "video": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"},
    "audio": {".mp3", ".flac", ".aac", ".wav"},
    "image": {".jpg", ".jpeg", ".png", ".gif"},
    "document": {".pdf", ".docx", ".txt", ".epub"},
}


def get_extension_group(ext):
    for group_name, extensions in EXTENSION_GROUPS.items():
        if ext.lower() in extensions:
            return group_name
    return None


def size_within_tolerance(size1, size2, tolerance=0.05):
    if size1 == 0 or size2 == 0:
        return False
    return abs(size1 - size2) / max(size1, size2) <= tolerance


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
    cleaned = cleaned.replace('_', ' ')
    cleaned = cleaned.replace('-', ' ')

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

    #print(f"Title: {title}")
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


def write_duplicates_to_json(duplicates, filename="duplicates.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(duplicates, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Duplicate data written to '{filename}'")


def get_file_size(file_path):
    """
    Returns the size of the file at the given path in bytes.
    Raises FileNotFoundError if the file does not exist.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")

    return os.path.getsize(file_path)


def get_file_extension(file_path):
    """
    Returns the file extension, including the leading dot.
    Example: 'file.txt' -> '.txt'
    If there is no extension, returns an empty string.
    """
    _, extension = os.path.splitext(file_path)
    return extension.lstrip('.')


def find_duplicate_directories(path):
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
        media_dir_dict[dirname] = {
            "cleaned_name": title,
            "year": year
        }

    duplicates = find_fuzzy_duplicates(media_dir_dict)
    return duplicates
    #write_duplicates_to_json(duplicates)


def find_fuzzy_file_duplicates(
    media_dict,
    title_threshold=0.8,
    size_tolerance=0.05,
    ignored_folders=None,
    ignored_extensions=None,
    verbose=True
):
    if ignored_folders is None:
        ignored_folders = []
    if ignored_extensions is None:
        ignored_extensions = []

    matches = defaultdict(set)
    items = list(media_dict.items())

    for i, (key1, data1) in enumerate(items):
        path1 = data1['path']
        ext1 = data1['extension'].lower()

        if any(ignored in path1 for ignored in ignored_folders):
            if verbose: print(f"Skipping (ignored folder): {path1}")
            continue
        if ext1 in ignored_extensions:
            if verbose: print(f"Skipping (ignored ext): {path1}")
            continue

        title1 = data1['cleaned_name']
        size1 = data1['size']
        year1 = data1.get('year')
        group1 = get_extension_group(ext1)

        for j in range(i + 1, len(items)):
            key2, data2 = items[j]
            path2 = data2['path']
            ext2 = data2['extension'].lower()

            if any(ignored in path2 for ignored in ignored_folders):
                continue
            if ext2 in ignored_extensions:
                continue

            title2 = data2['cleaned_name']
            size2 = data2['size']
            year2 = data2.get('year')
            group2 = get_extension_group(ext2)

            # First, check title similarity
            title_similarity = difflib.SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
            if title_similarity < title_threshold:
                if verbose:
                    print(f"Low similarity: '{title1}' vs '{title2}' — Title Ratio: {title_similarity:.2f}")
                continue

            # Then, check if both files belong to the same group (based on the first file)
            if not group1 or not group2 or group1 != group2:
                if verbose:
                    print(f"Extension group mismatch: {ext1} ({group1}) vs {ext2} ({group2})")
                continue

            # Optional: year check (if present)
            if year1 and year2 and year1 != year2:
                if verbose:
                    print(f"Year mismatch: {year1} vs {year2}")
                continue

            # Finally, check file size similarity
            #if not size_within_tolerance(size1, size2, size_tolerance):
            #    if verbose:
            #        print(f"Size mismatch: '{title1}' vs '{title2}' — Sizes: {size1} vs {size2}")
            #    continue

            # Record match
            match_key = f"{title1}" # ({year1 or 'unknown'}) [{group1}]"
            matches[match_key].update([path1, path2])

    # Final formatting
    for k in matches:
        matches[k] = sorted(matches[k])

    # Print matches
    if verbose:
        if not matches:
            print("No matches found.")
        else:
            for match_key, files in matches.items():
                if len(files) > 1:
                    print(f"\nDuplicate: {match_key}")
                    for f in files:
                        print(f"  - {f}")
    return matches


if __name__ == "__main__":
    print('finding duplicates')
    # Change this to the directory you want to start from
    for root, dirs, files in os.walk(path):
        for file in files:
            #print(f"file: {file}")
            full_path = os.path.join(root, file)
            #print(f"full_path: {full_path}")
            title = extract_title(file)
            title = to_uppercase(title)
            title = remove_release_groups(title)
            title = remove_after(title, '6CH')
            title = remove_after(title, '2CH')
            title = remove_after(title, 'RARBG')
            title = remove_after(title, 'AAC')
            title = remove_after(title, 'AC3')
            title = remove_after(title, 'AVC')
            title = remove_after(title, 'AVI')
            title = remove_after(title, 'BDRIP')
            title = remove_after(title, 'BRIP')
            title = remove_after(title, 'BDR9P')
            title = remove_after(title, 'H 264')
            title = remove_after(title, 'DTS')
            title = remove_after(title, 'DD5')
            title = remove_after(title, 'HDR10')
            title = remove_after(title, 'HEVC')
            title = remove_after(title, 'HDTVRIP')
            title = remove_after(title, 'EAC3')
            title = remove_after(title, 'WEB DL')
            title = remove_after(title, 'DL')
            title = remove_after(title, '270P')
            title = remove_after(title, '360P')
            title = remove_after(title, '480P')
            title = remove_after(title, '478P')
            title = remove_after(title, '696P')
            title = remove_after(title, '720P')
            title = remove_after(title, '752P')
            title = remove_after(title, '800P')
            title = remove_after(title, '812P')
            title = remove_after(title, '816P')
            title = remove_after(title, '868P')
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
            title = remove_after(title, 'MP4')
            title = remove_after(title, 'MKV')
            title = remove_after(title, 'M4V')
            title = remove_after(title, 'UHD')
            title = remove_after(title, 'DAT')

            title = remove_after(title, 'SRT')
            title = remove_after(title, 'TXT')
            title = remove_after(title, 'JPG')
            title = remove_after(title, 'PNG')
            title = remove_after(title, 'PSA')
            title = remove_after(title, 'REMASTERED')
            title = remove_suffix_and_after(title, '()')
            title = remove_suffix_and_after(title, '(')
            title = remove_exact_string(title, '[]')
            title = remove_suffix_and_after(title, '()')
            title = remove_char_if_at_end(title, '(')
            title = trim_string(title)
            title = remove_char_if_at_end(title, '-')
            #print(f"Original: {file}")
            #print(f"Title: {title}")
            year = find_year(file)
            full_path = os.path.join(root, file)
            media_file_dict[file] = {
                "cleaned_name": title,
                "year": year,
                "path": full_path,
                "size": get_file_size(full_path),
                "extension": get_file_extension(full_path)
            }

    duplicates = find_fuzzy_file_duplicates(
        media_dict=media_file_dict,
        title_threshold=0.20,  # More forgiving
        size_tolerance=0.05,  # Allow 10% difference
        ignored_folders=[],  # Don't ignore anything
        ignored_extensions=[],  # Don't ignore anything
        verbose=False  # Show debugging info
    )
    print(dict(duplicates))
    #return duplicates_files

