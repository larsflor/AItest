import csv
from faker import Faker

fake = Faker()

# Specify the file name
filename = "testdata.csv"

# Create and write to CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header
    writer.writerow(["Incident number", "Name"])
    
    # Write 1000 rows of data
    for i in range(1000):
        incident_number = 1000 + i
        name = fake.name()
        writer.writerow([incident_number, name])

print(f"File '{filename}' created successfully with 1000 rows of test data.")