import csv
import time
import requests
import json
import re

#This file parses between entries that it thinks are a name
# entries that it thinks are companies 
# and entries that it thinks are invalid
#Invalid entries include certain non company words, invalid us states (mexico or europe) and more.
# All results are split into the csv files in this folder

filename = "Split/input.csv"

state_to_abbreviation = { "Alabama": "al", "Alaska": "ak", "Arizona": "az", "Arkansas": "ar", "California": "ca", "Colorado": "co", "Connecticut": "ct", "Delaware": "de", "Florida": "fl", "Georgia": "ga", "Hawaii": "hi", "Idaho": "id", "Illinois": "il", "Indiana": "in", "Iowa": "ia", "Kansas": "ks", "Kentucky": "ky", "Louisiana": "la", "Maine": "me", "Maryland": "md", "Massachusetts": "ma", "Michigan": "mi", "Minnesota": "mn", "Mississippi": "ms", "Missouri": "mo", "Montana": "mt", "Nebraska": "ne", "Nevada": "nv", "New Hampshire": "nh", "New Jersey": "nj", "New Mexico": "nm", "New York": "ny", "North Carolina": "nc", "North Dakota": "nd", "Ohio": "oh", "Oklahoma": "ok", "Oregon": "or", "Pennsylvania": "pa", "Rhode Island": "ri", "South Carolina": "sc", "South Dakota": "sd", "Tennessee": "tn", "Texas": "tx", "Utah": "ut", "Vermont": "vt", "Virginia": "va", "Washington": "wa", "West Virginia": "wv", "Wisconsin": "wi", "Wyoming": "wy", "District of Columbia": "dc", "American Samoa": "as", "Guam": "gu", "Northern Mariana Islands": "mp", "Puerto Rico": "pr", "United States Minor Outlying Islands": "um", "Virgin Islands, U.S.": "vi" } 
keywords_to_ignore = ['llc', 'inc', 'airways', 'unconfirmed', 'corp', 'conseils', 'films', 'aviation', 'center', 'CV', "incorporated", "limited", "company", "co", ", ", "incoorperated", " .",]

def convert_state_to_iso(state_name): 
    # Convert the state name to title case to match the dictionary keys 
    state_name_title = state_name.title() 
    abbreviation = state_to_abbreviation.get(state_name_title) 
    if abbreviation: 
        return f"us_{abbreviation}"
    else: 
        return None

fields = []
data = []
print("hi")
# Reading CSV file
# with open(filename, 'r', encoding='utf-8') as input_file:
#     reader = csv.reader(input_file)
#     rows = list(reader)

# # Process the content (this step is optional and depends on your specific needs)

# # Write the CSV file with UTF-8 encoding
# with open("Split/output.csv", 'w', encoding='utf-8', newline='') as output_file:
#     writer = csv.writer(output_file)
#     writer.writerows(rows)


with open(filename, encoding='utf-8', errors='ignore') as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    i = 0
    for row in csvreader:
        print(i)
        i = i+1
        data.append(row)
        

numPeople = len(data)
print(numPeople)

printingFile = open("Split/print.csv", "w", newline='')
#writePrints = csv.writer(printingFile)


def process_person(row):
    full_name = row[9]
    state = row[10]

    words = full_name.lower().split()

    if("Unassigned" in state):
        return row, 2, False
    print(full_name , " " , state , ": ",file=printingFile) 
    
    if not any(keyword.lower() in full_name.lower() for keyword in ['LLC', 'Inc', 'LTD']) and (any(keyword.lower() in full_name.lower() for keyword in ['united states', 'FAA', 'Dept of Energy']) or any(word == keyword.lower() for word in words for keyword in ['National', 'State', 'Bank', 'army', 'Government', 'County', 'military', 'NASA', 'Unconfirmed', 'University', 'Department', 'Clinic','Ministries', 'District', 'Conservation', 'Agency', 'Patrol', 'Sheriffs', 'Governors', 'FAA/US DoT', 'Operations', 'Logistical Support', 'BlueCross', 'Authority', 'College', 'Police', 'Boeing'])):
        return row, 2, True
    elif(any(keyword.lower() in full_name.lower() for keyword in ['LLC', 'Inc', 'Corp', 'Conseils', 'Films', 'Aviation', 'Center', 'CV', 'Construction', 'LTD', 'air', 'LLP', 'Operator', 'Incoorperated', 'Aereos', 'Aerocom', 'Farms', 'Limited', 'Wings', 'Group', 'Wheels', 'Drilling', 'Financial', 'LIHTC', 'Trust', 'Industries', 'BV', 'X-Ray', 'Flying', 'Industrial', 'Transport', 'Companies', 'Company', 'Services', 'CareFlight', 'Flight', 'Aeronautics', 'Investment', 'Logistics', 'Distributing', 'Engineering', 'Engstrom', 'CareFlite', 'Development', 'Nation', 'Distributor' 'Borough'])) or any(word == keyword.lower() for word in words for keyword in ['Co', 'Air', 'Aircraft', 'Management', 'City', 'LC', 'Medical', 'Med', 'Health', 'Airways']):
        if '(' in full_name:
            parts = full_name.split('(')
            full_name = parts[0]
        
        stateVal = convert_state_to_iso(state)
        if stateVal == None:
            return row, 2, True
        else:
            return row, 1, True
    else:
        return row, 0, True
    
    



def main():
        file1 = open("Split/name.csv", "w", newline='')
        file2 = open("Split/company.csv", "w", newline='')
        file3 = open("Split/invalid.csv", "w", newline='')
        writer1 = csv.writer(file1)
        writer2 = csv.writer(file2)
        writer3 = csv.writer(file3)

        startVal = 0

        while startVal < (numPeople): 
            result, num, b = process_person(data[startVal])
            if b:
                print(startVal, num, file=printingFile)
                print(startVal)
            if num == 0:
                writer1.writerow(result)    
            if num == 1:
                writer2.writerow(result) 
            if num == 2:
                #print(result)
                writer3.writerow(result) 
            startVal+=1
        file1.close()
        file2.close()
        file3.close()
        print("hello")

main()
