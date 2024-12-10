import csv
import time
import requests
import json
import re
import difflib

#Given a large csv of input data. Parses all inputs. 
# If the input is a name, do nothing and add to clean.csv
# IF the input is a valid llc, use opencoorperates to find the best matching first and last name and add to clean.csv
# If the input is an invalid company (Ex: Amazon, Delta or gov agency/police dpt) add to problem.csv
# If the llc company is owned by another valid company add to llc.csv
# Print metrics to print.csv

filename = "CompanyName/input.csv"
apiKey = "OSruR0IccJVZMgxfzlC9"
apiToken = "api_token="+apiKey
version = "v0.4.8"

state_to_abbreviation = { "Alabama": "al", "Alaska": "ak", "Arizona": "az", "Arkansas": "ar", "California": "ca", "Colorado": "co", "Connecticut": "ct", "Delaware": "de", "Florida": "fl", "Georgia": "ga", "Hawaii": "hi", "Idaho": "id", "Illinois": "il", "Indiana": "in", "Iowa": "ia", "Kansas": "ks", "Kentucky": "ky", "Louisiana": "la", "Maine": "me", "Maryland": "md", "Massachusetts": "ma", "Michigan": "mi", "Minnesota": "mn", "Mississippi": "ms", "Missouri": "mo", "Montana": "mt", "Nebraska": "ne", "Nevada": "nv", "New Hampshire": "nh", "New Jersey": "nj", "New Mexico": "nm", "New York": "ny", "North Carolina": "nc", "North Dakota": "nd", "Ohio": "oh", "Oklahoma": "ok", "Oregon": "or", "Pennsylvania": "pa", "Rhode Island": "ri", "South Carolina": "sc", "South Dakota": "sd", "Tennessee": "tn", "Texas": "tx", "Utah": "ut", "Vermont": "vt", "Virginia": "va", "Washington": "wa", "West Virginia": "wv", "Wisconsin": "wi", "Wyoming": "wy", "District of Columbia": "dc", "American Samoa": "as", "Guam": "gu", "Northern Mariana Islands": "mp", "Puerto Rico": "pr", "United States Minor Outlying Islands": "um", "Virgin Islands, U.S.": "vi" } 
keywords_to_ignore = ['llc', 'inc', 'airways', 'unconfirmed', 'corp', 'conseils', 'films', 'aviation', 'center', 'CV', "incorporated", "limited", "company", "co", ", ", "incoorperated", " .", "corporation", "group", "the"]

#['LLC', 'Inc', 'Corp', 'Conseils', 'Films', 'Aviation', 'Center', 'CV', 'Construction', 'LTD', 'air', 'LLP', 'Operator', 'Incoorperated', 'Aereos', 'Aerocom', 'Farms', 'Limited', 'Wings', 'Group', 'Wheels', 'Drilling','LIHTC', 'BV', 'X-Ray', 'Flying', 'Industrial', 'Transport', 'Companies', 'Company', 'Services', 'CareFlight', 'Flight', 'Aeronautics', 'Investment', 'Logistics', 'Distributing', 'Engineering', 'Engstrom', 'CareFlite', 'Development', 'Nation', 'Distributor' 'Borough']
#['Co', 'Air', 'Aircraft', 'Management', 'City', 'LC', 'Medical', 'Med', 'Health', 'Airways']
printingFile = open("CompanyName/print.csv", "a")

def convert_state_to_iso(state_name): 
    # Convert the state name to title case to match the dictionary keys 
    state_name_title = state_name.title() 
    abbreviation = state_to_abbreviation.get(state_name_title) 
    if abbreviation: 
        return f"us_{abbreviation}"
    else: 
        raise ValueError(f"State name '{state_name}' not found")  

fields = []
data = []

# Reading CSV file
with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        row.append("")
        row.append("")
        row.append("")
        data.append(row)

fields.append("previousOwner") #-3
fields.append("agent_name") #-2
fields.append("error") #-1

numPeople = len(data)

def remove_keywords(name, keywords):
    # Create a regex pattern to match the keywords
    pattern = r'\b(?:' + '|'.join(re.escape(keyword.lower()) for keyword in keywords) + r')\b'
    # Remove the keywords and extra whitespace
    clean_name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    # Remove any extra spaces between words
    clean_name = re.sub(r'\s+', ' ', clean_name)
    return clean_name

def preprocess(text):
    # Remove spaces between characters for words that are broken down
    text = re.sub(r'\b(\w)\s+(\w)\b', r'\1\2', text)
    # Convert to lower case
    return text.lower()

def closest_match(target, options):
    target = preprocess(target)
    preprocessed_options = [preprocess(option) for option in options]
    
    # Get the closest match using difflib
    closest = difflib.get_close_matches(target, preprocessed_options, n=1)
    
    if closest:
        closest_match = closest[0]
        # Find the index of the closest match in the preprocessed options
        index = preprocessed_options.index(closest_match)
        return index
    else:
        return None

def find_company_url(data, target_name):
    clean_target_name = remove_keywords(target_name.lower(), keywords_to_ignore).lower()
    clean_target_name = clean_target_name.replace("-", ' ')
    clean_target_name = clean_target_name.replace(" .", '')
    clean_target_name = clean_target_name.replace(".", '')
    clean_target_name = clean_target_name.replace(",", '')
    clean_target_name = clean_target_name.replace("'", '')
    companies = data['results']['companies']
    companyArray = []
    objectArr = []
    for company_data in companies:
        company = company_data['company']
        clean_company_name = company['name'].lower().replace("-", ' ')
        clean_company_name = clean_company_name.replace(" .", '')
        clean_company_name = clean_company_name.replace(".", '')
        clean_company_name = clean_company_name.replace(",", '')
        clean_company_name = clean_company_name.replace("'", '')

        clean_company_name = remove_keywords(clean_company_name, keywords_to_ignore).lower()
        #print(f"Target Name: {target_name} Company Name: {company['name']}")
        #print(f"Target Name: {target_name} Company Name: {company['name']}", file=printingFile)
        #print(f"Clean Target Name: {clean_target_name} Clean Company Name: {clean_company_name}", file=printingFile)
        companyArray.append(clean_company_name)
        objectArr.append(company_data['company'])
        if clean_company_name == clean_target_name:
            return company['opencorporates_url']
    
    #choose closest name
    if(companyArray == []):
         return None
    
    index = closest_match(clean_target_name, companyArray)
    try:
        objectArr[index]['opencorporates_url']
    except:
        print("No link found for closest match", file=printingFile)
        #print("No link found for closest match")
        return None

    print(f"Target Name: {clean_target_name} Company Name: {companyArray[index]}", file=printingFile)
    return objectArr[index]['opencorporates_url']




def process_person(row):
    #full_name = row[20]
    full_name = row[9]
    print("Company name: " + full_name)
    print("Company name: " + full_name, file=printingFile)
    #print(row)
    state = row[10]
    if("Unassigned" in state):
        row[-1] = "unsassigned state"
        return row, 2
    
    #url = "https://api.opencorporates.com/v0.4/versions"+apiToken
    #sometimes companies have (state) in their name. Remove this for search.
    if '(' in full_name:
        parts = full_name.split('(')
        full_name = parts[0]
    #double ensure state is in the usa
    try:
        stateVal = convert_state_to_iso(state)
    except:
        row[-1] = "invalid state"
        return row, 2
    

    url = f"https://api.opencorporates.com/v0.4.8/companies/search?q={full_name.replace(' ', '+')}&jurisdiction_code="+ stateVal +"&per_page=100&normalise_company_name=true&"+apiToken
    #print(url)
    response = requests.get(url)
    json = response.json()

    #Edit for errors !!!
    newUrl = find_company_url(json, full_name)
    bool = True
    if(newUrl == None):
        if(json['results']['total_count'] == 1):
            try:
                newUrl = json['results']['companies']['company'][0]['opencorporates_url']
            except:
                row[-1] = "1 company with diff name, no url found"
                newUrl = None
                time.sleep(0.5)
                return row, 2
        elif(json['results']['total_count'] == 0):
            newUrl = f"https://api.opencorporates.com/v0.4.8/companies/search?q={full_name.replace(' ', '+')}"+ "&per_page=100&normalise_company_name=true&"+apiToken
            response = requests.get(url)
            json2 = response.json()
            if(json2['results']['total_count'] == 1):
                bool = False
                newUrl = json2['results']['companies']['company']['opencorporates_url']
            else:
                row[-1] = "0 company in state, no url found for country wide search (0 or more then 1 company found nationwide)"
                newUrl = None
                time.sleep(0.5)
                return row, 2
        if(newUrl == None):
            #print("not found")
            row[-1] = "Null url found after finding a url"
            time.sleep(0.5)
            return row, 2
    time.sleep(0.5)

    #Search for name of company
    #print(newUrl)
    if bool:
        searchURL = "https://api.opencorporates.com/v0.4.8/companies/" +"us_" + newUrl.split('/us_')[1] +"?" + apiToken
    else:
        searchURL = "https://api.opencorporates.com/v0.4.8/companies/" +"us_" + newUrl.split('/us_')[1] +"?" + apiToken
    #print(searchURL)
    response = requests.get(searchURL)
    json1 = response.json()
    #print(json1)
    #print("")

    agent_name = json1['results']['company']['agent_name']
    #modify row
    #name = ""
    #row[-3] = row[20]
    row[-3] = row[9]
    row[-2] = agent_name
    time.sleep(0.5)

    if(agent_name == None):
        row[-1] = "no agent name found for company url"
        return row, 2

    #if name is gov
    #if name is llc
    print(agent_name, file= printingFile)
    print("Agent Name: " + agent_name)
    words = agent_name.lower().split()
    if not any(keyword.lower() in agent_name.lower() for keyword in ['LLC', 'Inc', 'LTD']) and (any(keyword.lower() in full_name.lower() for keyword in ['united states', 'FAA', 'Dept of Energy']) or any(word == keyword.lower() for word in words for keyword in ['National', 'State', 'Bank', 'army', 'Government', 'County', 'military', 'NASA', 'Unconfirmed', 'University', 'Department', 'Clinic','Ministries', 'District', 'Conservation', 'Agency', 'Patrol', 'Sheriffs', 'Governors', 'FAA/US DoT', 'Operations', 'Logistical Support', 'BlueCross', 'Authority', 'College', 'Police', 'Boeing'])):
        row[-1] = "agent name found is government company"
        return row, 2
    elif (any(keyword.lower() in agent_name.lower() for keyword in ['LLC', 'Inc', 'Corp', 'Conseils', 'Films', 'Aviation', 'Center', 'CV', 'Construction', 'LTD', 'air', 'LLP', 'Operator', 'Incoorperated', 'Aereos', 'Aerocom', 'Farms', 'Limited', 'Wings', 'Group', 'Wheels', 'Drilling','LIHTC', 'BV', 'X-Ray', 'Flying', 'Industrial', 'Transport', 'Companies', 'Company', 'Services', 'CareFlight', 'Flight', 'Aeronautics', 'Investment', 'Logistics', 'Distributing', 'Engineering', 'Engstrom', 'CareFlite', 'Development', 'Nation', 'Distributor' 'Borough'])) or any(word == keyword.lower() for word in words for keyword in ['Co', 'Air', 'Aircraft', 'Management', 'City', 'LC', 'Medical', 'Med', 'Health', 'Airways']):
        row[-1] = "agent name found is llc"
        return row, 1
    else:
        row[-1] = "agent name found and is a name"
        return row, 0
    



def main():
        file1 = open("CompanyName/clean.csv", "a", newline='')
        file2 = open("CompanyName/llc.csv", "a", newline='')
        file3 = open("CompanyName/problem.csv", "a", newline='')
        writer1 = csv.writer(file1)
        writer2 = csv.writer(file2)
        writer3 = csv.writer(file3)

        startVal = 31398

        while startVal < (numPeople):
            #print("hi")
            print(startVal, ": ", file=printingFile)
            result, num = process_person(data[startVal])
            print("Location: ", num, file=printingFile)
            print(result[-1], file=printingFile)
            print("\n", file=printingFile)
            print(startVal, num)
            print(result[-1])
            
            if num == 0:
                writer1.writerow(result)    
            if num == 1:
                writer2.writerow(result) 
            if num == 2:
                writer3.writerow(result) 
            startVal+=1
        file1.close()
        file2.close()
        file3.close()

main()
