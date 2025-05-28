# Import necessary modules for file operations, string manipulation, and logging
import os
import string
import logging

# Set up logging configuration to track script execution and debug issues
# DEBUG level shows detailed information, format includes timestamp, level, and message
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_first_alphanumeric(domain):
    """
    Extract the first alphanumeric character from a domain name.
    
    This function iterates through each character in the domain until it finds
    the first character that is either a letter or a number, which is used
    for alphabetical sorting of domains.
    
    Args:
        domain (str): The domain name to analyze
        
    Returns:
        str: The first alphanumeric character (lowercase if letter), or '0' as default
    """
    # Iterate through each character in the domain string
    for char in domain:
        # Check if the character is alphanumeric (letter or digit)
        if char.isalnum():
            # Return lowercase version if it's a letter, otherwise return as-is for digits
            return char.lower() if char.isalpha() else char
    
    # Default return value if no alphanumeric character is found
    return '0'  # Default to '0' if no alphanumeric character is found


def remove_www(domain):
    """
    Remove the 'www.' prefix from a domain name if present.
    
    This function standardizes domain names by removing the common 'www.' prefix,
    making domains consistent for sorting and processing.
    
    Args:
        domain (str): The domain name that may have a 'www.' prefix
        
    Returns:
        str: The domain name without the 'www.' prefix
    """
    # Check if domain starts with 'www.' (case-insensitive) and remove it
    return domain[4:] if domain.lower().startswith('www.') else domain


def sort_domains(file_name):
    """
    Sort domains from a file into alphabetically organized files.
    
    This function reads a file containing domain names (one per line), removes
    'www.' prefixes, and sorts them into separate files based on their first
    alphanumeric character (0-9, a-z).
    
    Args:
        file_name (str): Path to the input file containing domain names
    """
    logging.info(f"Starting to process file: {file_name}")

    # Define the output directory for sorted domain files
    output_dir = 'sorted_domains'
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Output directory created: {output_dir}")

    # Initialize a dictionary to store domains for each alphanumeric character
    # string.digits gives '0123456789', string.ascii_lowercase gives 'abcdefghijklmnopqrstuvwxyz'
    domain_files = {char: [] for char in string.digits + string.ascii_lowercase}
    logging.debug(f"Initialized domain_files dictionary with {len(domain_files)} keys")

    # Read and process the input file
    try:
        # Open the input file for reading
        with open(file_name, 'r') as file:
            # Process each line in the file, keeping track of line numbers
            for line_num, line in enumerate(file, 1):
                # Remove whitespace from the beginning and end of the line
                domain = line.strip()
                
                # Only process non-empty lines
                if domain:
                    # Remove 'www.' prefix from the domain
                    domain_without_www = remove_www(domain)
                    # Get the first alphanumeric character for sorting
                    first_char = get_first_alphanumeric(domain_without_www)
                    # Add the cleaned domain to the appropriate list
                    domain_files[first_char].append(domain_without_www)
                    logging.debug(f"Processed domain: {domain_without_www} (first char: {first_char})")
                else:
                    # Log warning for empty lines
                    logging.warning(f"Empty line found at line {line_num}")

        logging.info(f"Finished reading input file. Total lines processed: {line_num}")
        
    except Exception as e:
        # Log any errors that occur during file reading
        logging.error(f"Error reading input file: {e}")
        return

    # Write sorted domains to separate output files
    for char in string.digits + string.ascii_lowercase:
        # Only create files for characters that have domains
        if domain_files[char]:
            # Create the output file path
            output_file = os.path.join(output_dir, f'{char}_domains.txt')
            
            try:
                # Open the output file for writing with UTF-8 encoding
                with open(output_file, 'w', encoding='utf-8') as out_file:
                    # Sort domains alphabetically (case-insensitive) and write each to a new line
                    for domain in sorted(domain_files[char], key=str.lower):
                        out_file.write(f"{domain}\n")
                
                # Log successful file creation
                logging.info(f"Created file: {output_file} with {len(domain_files[char])} domains")
                
            except Exception as e:
                # Log any errors that occur during file writing
                logging.error(f"Error writing to file {output_file}: {e}")
        else:
            # Log when no domains are found for a particular character
            logging.debug(f"No domains for character: {char}")

    logging.info(f"Domains have been sorted into files in the '{output_dir}' directory.")


# Main execution block - only runs when script is executed directly (not imported)
if __name__ == "__main__":
    # Define the input file path containing the formatted domains
    file_name = "./combined_single_files/formatted_domains.txt"
    
    # Call the main sorting function
    sort_domains(file_name)
