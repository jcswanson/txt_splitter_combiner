import os
import string
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_first_alphanumeric(domain):
    for char in domain:
        if char.isalnum():
            return char.lower() if char.isalpha() else '0'
    return '0'  # Default to '0' if no alphanumeric character is found


def remove_www(domain):
    return domain[4:] if domain.lower().startswith('www.') else domain


def sort_domains(file_name):
    logging.info(f"Starting to process file: {file_name}")

    # Create the output directory if it doesn't exist
    output_dir = 'sorted_domains'
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Output directory created: {output_dir}")

    # Dictionary to hold domains for each file
    domain_files = {char: [] for char in string.ascii_lowercase + string.digits}
    logging.debug(f"Initialized domain_files dictionary with {len(domain_files)} keys")

    # Read and sort domains
    try:
        with open(file_name, 'r') as file:
            for line_num, line in enumerate(file, 1):
                domain = line.strip()
                if domain:
                    domain_without_www = remove_www(domain)
                    first_char = get_first_alphanumeric(domain_without_www)
                    domain_files[first_char].append(domain_without_www)
                    logging.debug(f"Processed domain: {domain_without_www} (first char: {first_char})")
                else:
                    logging.warning(f"Empty line found at line {line_num}")

        logging.info(f"Finished reading input file. Total lines processed: {line_num}")
    except Exception as e:
        logging.error(f"Error reading input file: {e}")
        return

    # Write sorted domains to files
    for char in string.ascii_lowercase + string.digits:
        if domain_files[char]:
            output_file = os.path.join(output_dir, f'{char}_domains.txt')
            try:
                with open(output_file, 'w', encoding='utf-8') as out_file:
                    for domain in sorted(domain_files[char], key=str.lower):
                        out_file.write(f"{domain}\n")
                logging.info(f"Created file: {output_file} with {len(domain_files[char])} domains")
            except Exception as e:
                logging.error(f"Error writing to file {output_file}: {e}")
        else:
            logging.debug(f"No domains for character: {char}")

    logging.info(f"Domains have been sorted into files in the '{output_dir}' directory.")


# Usage
if __name__ == "__main__":
    file_name = "./combined_single_files/formatted_domains.txt"
    sort_domains(file_name)
