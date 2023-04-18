"""
Usage: python3 generate_ja_conjugations.py <input file name> <output file name>

Input file name must be a sequential JMDict file.
Something like:
    [["識しませんでした", "しるしませんでした", "v5s", "v5", 10, ["écrire", "coucher sur le papier", "noter"], 1223140, ""], ..., ["高めなくて", "たかめなくて", "v1 vt", "v1", 706, ["élever", "augmenter", "hausser", "surélever"], 1283240, "P ichi news"], ["高めるな", "たかめるな", "v1 vt", "v1", 706, ["élever", "augmenter", "hausser", "surélever"], 1283240, "P ichi news"]]
"""
from pykatsuyou import getInflections
import sys
import json

input_file = sys.argv[1]
output_file = sys.argv[2]
with open(input_file, "r") as in_f:
    # Keep only verbs
    termbankv = tuple(filter(lambda x: x[2].startswith("v"), eval(in_f.read())))
    # Remove suru and zuru verbs
    termbankv = tuple(filter(lambda x: x[2][1] != 'z', termbankv))
    termbankv = tuple(filter(lambda x: x[2][1] != 's', termbankv))


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

conj_ve = []
for entry in termbankv:
    try:
        conj_ve += generate_conjugated_entries(entry)
    except IndexError:
        print(entry[0])
        continue

with open(output_file, "w") as out_f:
    # json.dump(out_f, ...) doesn't work for some reason...
    out_f.write(json.dumps(conj_ve, ensure_ascii=False))
