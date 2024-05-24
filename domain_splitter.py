import os
import re
import string



# Create a new directory to store the sorted files
sorted_dir = './sorted-black-domains'
if not os.path.exists(sorted_dir):
    os.makedirs(sorted_dir)



# Define a dictionary to hold the domains for each letter
letter_domains = {}
for letter in string.ascii_lowercase + '0123456789':
    letter_domains[letter] = set()

print("Letter domains dictionary created")

# Ingest a directory of text files
directory = './block_list_files'
print(f"Looking for input files in directory {directory}")
for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        print(f"Found input file {filename}")
        with open(os.path.join(directory, filename), 'r') as infile:
            for line in infile:
                print(f"Processing line: {line}")
                # Strip away the first batch of characters and all spaces until the second batch of characters
                # line = re.sub(r'^\S*\s*', '', line)
                domain = line.replace('www.', '')
                print(f"Extracted domain: {domain}")
                        # Add the domain to the appropriate set
                letter = domain[0].lower()
                if letter in letter_domains:
                    print(f"First letter of domain is a valid letter or number: {letter}")
                    letter_domains[letter].add(domain)


print("Finished processing input files")

# Save the sorted domains to files
for letter, domains in letter_domains.items():
    with open(os.path.join(sorted_dir, f'{letter}_domains.txt'), 'w') as outfile:
        for domain in sorted(domains):
            print(f"Writing domain {domain} to file {letter}_domains.txt")
            outfile.write(f'{domain}')

print("Script finished")