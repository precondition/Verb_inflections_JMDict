"""
Usage: python3 generate_ja_conjugations.py <input file name> <output file name>

Input file name must be a sequential JMDict file.
Something like:
    [["識しませんでした", "しるしませんでした", "v5s", "v5", 10, ["écrire", "coucher sur le papier", "noter"], 1223140, ""], ..., ["高めなくて", "たかめなくて", "v1 vt", "v1", 706, ["élever", "augmenter", "hausser", "surélever"], 1283240, "P ichi news"], ["高めるな", "たかめるな", "v1 vt", "v1", 706, ["élever", "augmenter", "hausser", "surélever"], 1283240, "P ichi news"]]
"""
from patched_pykatsuyou import getInflections
import sys
import json

def hiragana_inflection(entry: list, inflection: str) -> str:
    """
    Takes an inflected verb and uses info of the dictionary entry
    to infer its hiragana reading.
    """
    base_verb = entry[0]
    base_verb_reading = entry[1]
    if base_verb_reading == '':
        return inflection
    i = -1
    while -i < len(base_verb)+1 and base_verb[i] == base_verb_reading[i]:
        i -= 1
    root_length = len(base_verb)+i+1
    return base_verb_reading[:i+1] + inflection[root_length:]

def generate_conjugated_entries(entry: list) -> list:
    entries = []
    base_verb = entry[0]
    base_verb_reading = entry[1]
    for inflection in getInflections(base_verb)["list"]:
        entries.append([inflection, hiragana_inflection(entry, inflection)] + entry[2:])
    return entries[1:] # Ignore base form

input_file = sys.argv[1]
output_file = sys.argv[2]
with open(input_file, "r", encoding="utf-8") as in_f:
    termbank_reader = json.load(in_f)

conj_ve = []
for entry in termbank_reader:
    # Ignore entries where the head word is only a single word.
    # All verbs in contemporary japanese are at least 2 characters.
    if len(entry[0]) == 1:
        continue
    part_of_speech: str = entry[2]
    # Ignore non-verbs
    if not part_of_speech.startswith("v"):
        continue
    # Ignore suru and zuru verbs
    if part_of_speech[1] == 'z' or part_of_speech[1] == 's':
        continue
    try:
        conj_ve += generate_conjugated_entries(entry)
    except IndexError as err:
        # Most likely the igo tagger that failed to parse the word correctly.
        # For example, it breaks down the verb "薫じる" into three components
        # even though it is a single component.
        print("Skipping", entry[0], "because Igo failed to parse it correctly.")
        continue

with open(output_file, "w") as out_f:
    # json.dump(out_f, ...) doesn't work for some reason...
    out_f.write(json.dumps(conj_ve, ensure_ascii=False))
