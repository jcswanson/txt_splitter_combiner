import re


def process_domains(input_file, output_file):
    domain_pattern = re.compile(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Remove leading/trailing whitespace and any IP addresses
            line = line.strip().split()[-1]

            # Extract the domain using regex
            match = domain_pattern.search(line)
            if match:
                domain = match.group(1)
                # Write the processed domain to the output file
                outfile.write(f"www.{domain}\n")


if __name__ == "__main__":
    # Specify the input and output files
    input_file = './block_list_files/black-list-all-in-one-v2.txt'
    output_file = 'formatted_domains.txt'

    process_domains(input_file, output_file)
    print(f"Processing complete. Results saved to {output_file}")
