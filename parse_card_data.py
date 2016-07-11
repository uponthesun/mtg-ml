#!/usr/bin/env python

# Expected input: JSON output from https://deckbrew.com/
# Expected output: A CSV file that follows the AML data format http://docs.aws.amazon.com/machine-learning/latest/dg/understanding-the-data-format-for-amazon-ml.html
# Example usage: ./parse_card_data.py sample_creature_data.txt

import argparse
import json
import sys
import logging
import re

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        # obj is unicode
        return unicode(obj).encode('unicode-escape')

# Handles conversion of unicode characters, removing newlines, and enclosing the value in quotes if we've specified that the column should be.
def sanitizeValue(value, quotedColumns, columnName):
	strValue = safe_str(value).lower()
	# Remove newlines.
	returnValue = strValue.replace('\n', ' ').replace('\r', ' ').replace('\\u2212', '-').replace('\\u2014', '-') # convert unicode minus sign into ascii one.

	# Reminder text is always enclosed in one pair of parens. Parens are never nested.
	if (args.clean_reminder_text):
		returnValue = re.sub(r'\(.*?\)', "", returnValue)
	if (args.keywords_only and columnName == 'text'):
		foundKeywords = map(lambda w: w.replace(' ', ''), filter(lambda w: w in returnValue, keywords))
		returnValue = ' '.join(foundKeywords)
	# Enclose in double quotes if the string contains the column separator character.
	if (columnName in quotedColumns):
		returnValue = '"{}"'.format(returnValue)
	return returnValue

# The idea of this function is that it expands a card property that is a list of enumerated values, e.g. colors,
# into a binary attribute for each possible options. TODO: make this not suck
def addListCol(values, card, enumToBinaryColumns, key, sep):
	if(key in card):
		cardValues = card[key]
	else:
		cardValues = []	

	for option in enumToBinaryColumns[key]:
		if(option in cardValues):
			values.append("1")
		else:
			values.append("0")

def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
	parser.add_argument('--clean-reminder-text', action='store_true')
	parser.add_argument('--keywords-only', action='store_true')
	return parser.parse_args()

args = parseArgs()

# Read input file contents and parse them into a list of JSON objects.
inputFile = args.infile
allLines = inputFile.read()
inputFile.close()
cardList = json.loads(allLines)

#columns = ['name', 'cmc', 'power', 'toughness', 'types', 'subtypes', 'colors', 'text']
#columns = ['name', 'cmc', 'power', 'toughness', 'text']
columns = ['name', 'cmc', 'colors', 'subtypes', 'power', 'toughness', 'text']
#columns = ['name', 'cmc', 'power', 'toughness']
#columns = ['name', 'cmc', 'types', 'colors', 'text', 'subtypes']
quotedColumns = ['name', 'text', 'types', 'subtypes','colors']
#keywords = ['Deathtouch', 'Defender', 'Double strike', 'Enchant', 'Equip', 'First strike', 'Flash', 'Flying', 'Haste', 'Hexproof', 'Indestructible', 'Lifelink', 'Menace', 'Prowess', 'Reach', 'Scry', 'Trample', 'Vigilance', 'Fear', 'Intimidate']
keywords = ['Deathtouch', 'Defender', 'Double Strike', 'Enchant', 'Equip', 'First Strike', 'Flash', 'Flying', 'Haste', 'Hexproof', 'Indestructible', 'Lifelink', 'Menace', 'Prowess', 'Reach', 'Trample', 'Vigilance', 'Absorb', 'Affinity', 'Amplify', 'Annihilator', 'Aura Swap', 'Awaken', 'Banding', 'Battle Cry', 'Bestow', 'Bloodthirst', 'Bushido', 'Buyback', 'Cascade', 'Champion', 'Changeling', 'Cipher', 'Conspire', 'Convoke', 'Cumulative Upkeep', 'Cycling', 'Dash', 'Delve', 'Dethrone', 'Devoid', 'Devour', 'Dredge', 'Echo', 'Entwine', 'Epic', 'Evoke', 'Evolve', 'Exalted', 'Exploit', 'Extort', 'Fading', 'Fear', 'Flanking', 'Flashback', 'Forecast', 'Fortify', 'Frenzy', 'Fuse', 'Graft', 'Gravestorm', 'Haunt', 'Hidden Agenda', 'Hideaway', 'Horsemanship', 'Infect', 'Ingest', 'Intimidate', 'Kicker', 'Landhome', 'Landwalk', 'Level Up', 'Living Weapon', 'Madness', 'Megamorph', 'Miracle', 'Modular', 'Morph', 'Myriad', 'Ninjutsu', 'Offering', 'Outlast', 'Overload', 'Persist', 'Phasing', 'Poisonous', 'Protection', 'Provoke', 'Prowl', 'Rampage', 'Rebound', 'Recover', 'Reinforce', 'Renown', 'Replicate', 'Retrace', 'Ripple', 'Scavenge', 'Skulk', 'Shadow', 'Shroud', 'Soulbond', 'Soulshift', 'Splice', 'Split Second', 'Storm', 'Substance', 'Sunburst', 'Surge', 'Suspend', 'Totem Armor', 'Transfigure', 'Transmute', 'Tribute', 'Undying', 'Unearth', 'Unleash', 'Vanishing', 'Wither']
keywords = map(lambda w: w.lower(), keywords)
sep = ","
# Format the header line which contains all the column names.
# TODO: make this more robust
columnNames = sep.join(columns);

# Print header line
print columnNames

# Print observation lines
for card in cardList:
	# The list of attributes of a card we care about. At the end of each iteration, gets joined and output as a csv line.
	values = []
	try:
		# For each card JSON object, iterate through the columns we care about and add those to values.
		for col in columns:			
			if(not col in card):
                                if(col in quotedColumns):
				    colValue = ""
                                else:
                                    colValue = -1
			# If the field is a list, concatenate the values.
			elif(isinstance(card[col], list)):
				colValue = " ".join(card[col])
			else:
				colValue = card[col]
			values.append(sanitizeValue(colValue, quotedColumns, col))
		# Output as CSV line.
		print sep.join(values)
	except Exception:
		logging.error("Failed to parse: {}".format(str(card)))
		raise
