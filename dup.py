import csv

#This file parses duplicate entries as there is no need to store get their information twice!

# Define the input and output file names
input_filename = 'duplicates.csv'
output_filename = 'out.csv'

# Initialize lists to store fields and data
fields = []
data = []

# Reading the CSV file
with open(input_filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)
    for row in csvreader:
        data.append(row)

# Find the indexes of the 'Owner State' and 'Agent Name' columns
owner_state_index = fields.index('Owner State')
agent_name_index = fields.index('agent_name')

# Create a set to keep track of unique (Owner State, Agent Name) pairs
unique_rows = set()
filtered_data = []

for row in data:
    # Create a tuple of the values from 'Owner State' and 'Agent Name'
    unique_key = (row[owner_state_index], row[agent_name_index])
    # Check if this tuple is already in the set
    if unique_key not in unique_rows:
        unique_rows.add(unique_key)
        filtered_data.append(row)
    else:
        print(f"Duplicate entrie: {unique_key}")
    

# Writing to the output CSV file
with open(output_filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the fields (column names)
    csvwriter.writerow(fields)
    # Write the filtered data
    csvwriter.writerows(filtered_data)

# Calculate the number of unique people
numPeople = len(filtered_data)
print(f"Number of unique entries: {numPeople}")