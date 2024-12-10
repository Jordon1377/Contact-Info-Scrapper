import csv

#This file formats a csv input so that rows for phone number and emails are added and ordered correctly

# Define the input and output file names
input_filename = 'namesFormat.csv'
output_filename = 'out.csv'

# Initialize lists to store fields and data
data = []

# Reading the CSV file
with open(input_filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        data.append(row)

# Find the indexes of the 'Owner State' and 'Agent Name' columns
for row in data:
    row.append(row[9])  # Placeholder for phone numbers
    row.append(row[9])  # Placeholder for emails
    row.append("No llc already was a name")  # Placeholder for emails

# Writing to the output CSV file
with open(output_filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the fields (column names)
    # Write the filtered data
    csvwriter.writerows(data)

# Calculate the number of unique people
numPeople = len(data)
print(f"Number of unique entries: {numPeople}")