#!/usr/bin/env python
import os
import csv
import glob
import sys

# arguments
if len(sys.argv)<2:
    print('Usage: python3 xref_csv.py <LDRAW_DIR> <CSV_FILE>')
    exit()

LDRAW_DIR = sys.argv[1] #'/media/data/Projects/blender/Lego/ldraw/'
INVENTORY_FILENAME = sys.argv[2] #'Brickset-inventory-75192-1.csv'

LDRAW_PARTS = LDRAW_DIR + 'ldraw/parts/'
MY_PARTS = LDRAW_DIR + 'mycollection/'
UNOFFICIAL_PARTS = LDRAW_DIR + 'unof/'

#test LDRAW_DIR
if not(os.path.isdir(LDRAW_PARTS)):
    print(f'Cannot find LDraw directory {LDRAW_PARTS}')
    exit()
if not(os.path.isdir(MY_PARTS)):
    print(f'Cannot find mycollection directory {MY_PARTS}')
    exit()
if not(os.path.isdir(UNOFFICIAL_PARTS)):
    print(f'Cannot find unofficial parts directory {UNOFFICIAL_PARTS}')
    exit()

#open inventory csv
# full path or local file?
argpath = os.path.dirname(INVENTORY_FILENAME)
argfile = os.path.basename(INVENTORY_FILENAME)
if argpath == '':
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
else:
    CURRENT_PATH = argpath
    INVENTORY_FILENAME = argfile

# validate local file
if not(os.path.isfile(CURRENT_PATH + '/' + INVENTORY_FILENAME)):
    if not(os.path.isfile(INVENTORY_FILENAME)):
        print(f'Cannot open CSV file {CURRENT_PATH}/{INVENTORY_FILENAME}')
        exit()

# open database csv file
try:
    incsvfile = open(CURRENT_PATH + '/' + INVENTORY_FILENAME, 'r')
except:
    print(f"Could not open input CSV file {CURRENT_PATH}/{INVENTORY_FILENAME}")
    exit()
# create the output xref file
try:
    outcsvfile = open(CURRENT_PATH + '/' + INVENTORY_FILENAME.replace('.csv','XREF.csv'), 'w')
except:
    print(f"Could not open output CSV file {CURRENT_PATH}/{INVENTORY_FILENAME.replace('.csv','XREF.csv')}")
    exit()

#bind csv object to file
csv_reader = csv.reader(incsvfile)
csv_writer = csv.writer(outcsvfile)

#initialize stats
stats_partscount = 0
stats_partsfound = 0
stats_partsnotfound = 0

firstrow = True
for row in csv_reader:
    if len(row) == 0:
        break
    #append row 9 and 10 if missing
    if len(row) < 10:
        row.append("")
    if len(row) < 11:
        row.append("")
    if firstrow == False:
        searchparts = []
        # from original csv file
        searchparts.append(row[1])
        if row[4] != '':
            searchparts.append(row[5])
        # try alternate parts from column j
        for a in row[9].split(','):
            if (len(a) > 0):
                searchparts.append(a.strip())
        matched = False
        for trypart in searchparts:
            #look for parts in my parts
            for foundfile in glob.glob(f'{MY_PARTS}**/{trypart}.*', recursive=True):
                # set path to column K
                row[10] = foundfile
                row[9] = trypart
                matched = True
                break
            if not(matched):
                #look for parts in ldraw
                for foundfile in glob.glob(f'{LDRAW_PARTS}**/{trypart}.*', recursive=True):
                    # set path to column K
                    row[10] = foundfile
                    row[9] = trypart
                    matched = True
                    break
            if not(matched):
                #look for parts in unofficial
                for foundfile in glob.glob(f'{UNOFFICIAL_PARTS}**/{trypart}.*', recursive=True):
                    # set path to column K
                    row[10] = foundfile
                    row[9] = trypart
                    matched = True
                    break
            if (matched):
                break
        csv_writer.writerow(row)
        # update stats
        stats_partscount += 1
        if (matched):
            stats_partsfound += 1
        else:
            stats_partsnotfound += 1
    if (firstrow):
        row[9] = "Use Part"
        row[10] = "Path"
        csv_writer.writerow(row)
    firstrow = False

incsvfile.close()
outcsvfile.close()
print(f'Parts Total: {stats_partscount}\nFound: {stats_partsfound}\nNot Found: {stats_partsnotfound}\n')
