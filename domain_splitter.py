# Import necessary modules for file operations, regex processing, and string manipulation
import os
import re
import string

# Create a new directory to store the sorted domain files
sorted_dir = './sorted-black-domains'
# Check if the directory doesn't exist, then create it
if not os.path.exists(sorted_dir):
    os.makedirs(sorted_dir)

# Define a dictionary to hold the domains for each letter/number
# This will organize domains by their first character (a-z, 0-9)
letter_domains = {}

# Initialize the dictionary with empty sets for each alphanumeric character
# string.ascii_lowercase gives 'abcdefghijklmnopqrstuvwxyz'
# '0123456789' gives all digits
# Each key maps to an empty set (sets automatically handle duplicates)
for letter in string.ascii_lowercase + '0123456789':
    letter_domains[letter] = set()

print("Letter domains dictionary created")

# Define the input directory containing the blocklist files to process
directory = './block_list_files'
print(f"Looking for input files in directory {directory}")

# Process all .txt files in the input directory
for filename in os.listdir(directory):
    # Only process files with .txt extension
    if filename.endswith('.txt'):
        print(f"Found input file {filename}")
        
        # Open and read each file
        with open(os.path.join(directory, filename), 'r') as infile:
            # Process each line in the file
            for line in infile:
                print(f"Processing line: {line}")
                
                # Strip away the first batch of characters and all spaces until the second batch of characters
                # This line is commented out - it would remove everything up to the first space
                # line = re.sub(r'^\S*\s*', '', line)
                
                # Remove 'www.' prefix from the domain for consistent formatting
                domain = line.replace('www.', '')
                print(f"Extracted domain: {domain}")
                
                # Get the first character of the domain (converted to lowercase)
                letter = domain[0].lower()
                
                # Check if the first character is a valid letter or number
                if letter in letter_domains:
                    print(f"First letter of domain is a valid letter or number: {letter}")
                    # Add the domain to the appropriate set (sets automatically handle duplicates)
                    letter_domains[letter].add(domain)

print("Finished processing input files")

# Save the sorted domains to separate files, one for each letter/number
for letter, domains in letter_domains.items():
    # Create output file path for this letter/number
    output_file_path = os.path.join(sorted_dir, f'{letter}_domains.txt')
    
    # Open the output file for writing
    with open(output_file_path, 'w') as outfile:
        # Sort the domains alphabetically and write each one to the file
        for domain in sorted(domains):
            print(f"Writing domain {domain} to file {letter}_domains.txt")
            # Write the domain to the file (note: domain already includes newline from original)
            outfile.write(f'{domain}')

print("Script finished")