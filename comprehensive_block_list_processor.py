#!/usr/bin/env python3
"""
Comprehensive Block List Processor

This script is the main processing engine for creating comprehensive domain blocklists
from multiple sources. It provides a complete solution for:

1. Processing ALL files in the block_list_files directory (local sources)
2. Downloading and processing web-based blocklists (remote sources)
3. Creating formatted_domains.txt with domains in 'www.domain.com' format
4. Creating alphabetically sorted domain files in 'domain.com' format (without www)
5. Applying whitelist filtering to exclude allowed domains
6. Comprehensive logging and verification of results
7. Deduplication and proper sorting of all domains

The script replaces the need to run multiple separate scripts and ensures
consistent formatting and complete inclusion of all sources.

Usage:
    python comprehensive_block_list_processor.py

Output Files:
    - combined_single_files/formatted_domains.txt: All domains with www. prefix
    - sorted_domains/*.txt: Alphabetically sorted files without www. prefix
    - block_list_processing.log: Detailed processing log
"""

# Import necessary modules for various operations
import os          # Operating system interface for file/directory operations
import re          # Regular expressions for pattern matching and text processing
import requests    # HTTP library for downloading web content
import string      # String constants and utilities for character sets
import logging     # Logging framework for tracking execution and debugging
from urllib.parse import urlparse  # URL parsing utilities

# Configure comprehensive logging system
# This creates both file and console output with timestamps and log levels
logging.basicConfig(
    level=logging.INFO,  # Set minimum log level to INFO (excludes DEBUG messages)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Include timestamp, level, and message
    handlers=[
        # Write all logs to a file for permanent record
        logging.FileHandler('block_list_processing.log'),
        # Also display logs in console for real-time monitoring
        logging.StreamHandler()
    ]
)

def is_github_url(url):
    """
    Determine if a given URL is from GitHub (github.com or raw.githubusercontent.com).
    
    This function is used to identify GitHub URLs so they can be converted to raw
    content URLs for direct file downloading.
    
    Args:
        url (str): The URL to check
        
    Returns:
        bool: True if the URL is from GitHub, False otherwise
    """
    # Parse the URL to extract its components (scheme, netloc, path, etc.)
    parsed_url = urlparse(url)
    # Check if the network location (domain) matches GitHub domains
    return parsed_url.netloc == "github.com" or parsed_url.netloc == "raw.githubusercontent.com"

def get_raw_content(url):
    """
    Download raw text content from a URL with GitHub URL conversion support.
    
    This function handles downloading content from web URLs, with special handling
    for GitHub URLs to convert them to raw content format. It includes error
    handling and timeout protection.
    
    Args:
        url (str): The URL to download content from
        
    Returns:
        str: The raw text content from the URL, or empty string if download fails
    """
    # Convert GitHub URLs to raw content format for direct file access
    if is_github_url(url) and "raw" not in url:
        # Replace github.com with raw.githubusercontent.com for direct file access
        url = url.replace("github.com", "raw.githubusercontent.com")
        # Remove /blob/ from the path as it's not needed for raw content
        url = url.replace("/blob/", "/")
    
    try:
        # Make HTTP GET request with timeout protection
        response = requests.get(url, timeout=30)
        # Raise an exception for HTTP error status codes (4xx, 5xx)
        response.raise_for_status()
        # Return the text content of the response
        return response.text
    except Exception as e:
        # Log any errors that occur during download
        logging.error(f"Failed to download {url}: {e}")
        # Return empty string on failure to allow processing to continue
        return ""

def process_line(line, domain_pattern):
    """
    Extract a valid domain from a line of text using regex pattern matching.
    
    This function handles various blocklist formats by extracting domains from
    lines that may contain IP addresses, comments, or other prefixes. It's designed
    to work with common blocklist formats like hosts files.
    
    Args:
        line (str): A line of text that may contain a domain
        domain_pattern (re.Pattern): Compiled regex pattern to match domains
        
    Returns:
        str or None: The extracted domain if found and valid, None otherwise
    """
    # Skip comment lines (starting with #) and empty lines
    if line.strip().startswith('#') or not line.strip():
        return None
    
    # Split the line into parts to handle formats like "0.0.0.0 domain.com"
    parts = line.strip().split()
    if not parts:
        return None
    
    # Take the last part, which is usually the domain in blocklist formats
    line = parts[-1]
    
    # Use regex to search for a valid domain pattern in the line
    match = domain_pattern.search(line)
    if match:
        # Return the first captured group (the domain without protocol/www)
        return match.group(1)
    return None

def load_whitelist(whitelist_file):
    """
    Load domains from a whitelist file into a set for fast lookup operations.
    
    The whitelist contains domains that should be excluded from blocking, even
    if they appear in blocklists. This function loads them with www. prefix
    for consistency with the main domain format.
    
    Args:
        whitelist_file (str): Path to the whitelist file
        
    Returns:
        set: Set of whitelisted domains with www. prefix for fast lookup
    """
    # Initialize empty set to store whitelisted domains
    whitelist = set()
    
    # Check if the whitelist file exists before trying to read it
    if os.path.exists(whitelist_file):
        logging.info(f"Loading whitelist from {whitelist_file}")
        
        # Open the file with UTF-8 encoding for proper character handling
        with open(whitelist_file, 'r', encoding='utf-8') as wfile:
            # Process each line in the whitelist file
            for line in wfile:
                # Remove whitespace and get the clean domain
                domain = line.strip()
                if domain:
                    # Add www. prefix for consistency with main domain format
                    whitelist.add(f"www.{domain}")
        
        logging.info(f"Loaded {len(whitelist)} whitelisted domains")
    else:
        # Log warning if whitelist file is not found
        logging.warning(f"Whitelist file not found: {whitelist_file}")
    
    return whitelist

def load_custom_blocklist(custom_blocklist_file, domain_pattern):
    """
    Load additional domains from a custom blocklist file with flexible parsing.
    
    This function handles custom blocklist files that may have various formats,
    attempting both regex extraction and direct line processing to maximize
    domain capture from different file formats.
    
    Args:
        custom_blocklist_file (str): Path to the custom blocklist file
        domain_pattern (re.Pattern): Compiled regex pattern to match domains
        
    Returns:
        set: Set of custom domains to block with www. prefix
    """
    # Initialize empty set to store custom domains
    custom_domains = set()
    
    # Check if the custom blocklist file exists
    if os.path.exists(custom_blocklist_file):
        logging.info(f"Loading custom blocklist from {custom_blocklist_file}")
        
        # Open the file with UTF-8 encoding
        with open(custom_blocklist_file, 'r', encoding='utf-8') as cfile:
            # Process each line in the custom blocklist
            for line in cfile:
                # Try to extract domain using the standard processing function
                domain = process_line(line, domain_pattern)
                if domain:
                    # Add www. prefix and add to custom domains set
                    custom_domains.add(f"www.{domain}")
                else:
                    # If regex extraction fails, try to use the line directly
                    clean_domain = line.strip()
                    # Skip empty lines and comments
                    if clean_domain and not clean_domain.startswith('#'):
                        # Add www. prefix if not already present
                        if not clean_domain.startswith('www.'):
                            clean_domain = f"www.{clean_domain}"
                        custom_domains.add(clean_domain)
        
        logging.info(f"Loaded {len(custom_domains)} custom domains")
    else:
        # Log warning if custom blocklist file is not found
        logging.warning(f"Custom blocklist file not found: {custom_blocklist_file}")
    
    return custom_domains

def process_all_local_files(input_directory, domain_pattern):
    """
    Process ALL .txt files in the input directory to extract domains.
    
    This function ensures that every .txt file in the block_list_files directory
    is processed, providing comprehensive coverage of all local blocklist sources.
    It tracks processing statistics for each file.
    
    Args:
        input_directory (str): Directory containing local blocklist files
        domain_pattern (re.Pattern): Compiled regex pattern to match domains
        
    Returns:
        tuple: (set of unique domains, list of processing statistics)
    """
    # Initialize set to store all unique domains from local files
    unique_domains = set()
    # List to track processing statistics for each file
    processed_files = []
    
    # Verify that the input directory exists
    if not os.path.exists(input_directory):
        logging.error(f"Input directory not found: {input_directory}")
        return unique_domains, processed_files
    
    # Get all .txt files in the directory for processing
    txt_files = [f for f in os.listdir(input_directory) if f.endswith('.txt')]
    logging.info(f"Found {len(txt_files)} .txt files in {input_directory}")
    
    # Process each .txt file in the directory
    for filename in txt_files:
        # Create full path to the input file
        input_file = os.path.join(input_directory, filename)
        logging.info(f"Processing file: {input_file}")
        
        try:
            # Open file with UTF-8 encoding and ignore encoding errors for robustness
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
                line_count = 0      # Track total lines processed
                domain_count = 0    # Track domains successfully extracted
                
                # Process each line in the file
                for line in infile:
                    line_count += 1
                    # Extract domain from the line using regex pattern
                    domain = process_line(line, domain_pattern)
                    if domain:
                        # Add www. prefix and add to unique domains set
                        unique_domains.add(f"www.{domain}")
                        domain_count += 1
                
                # Log processing statistics for this file
                logging.info(f"  - Processed {line_count} lines, extracted {domain_count} domains")
                # Store statistics for reporting
                processed_files.append((filename, line_count, domain_count))
                
        except Exception as e:
            # Log any errors that occur during file processing
            logging.error(f"Error processing {input_file}: {e}")
    
    return unique_domains, processed_files

def process_web_sources(urls, domain_pattern):
    """
    Process web-based blocklist sources to extract domains.
    
    This function downloads content from web URLs and extracts domains using
    the same processing logic as local files. It handles download failures
    gracefully and continues processing other sources.
    
    Args:
        urls (list): List of URLs to download blocklists from
        domain_pattern (re.Pattern): Compiled regex pattern to match domains
        
    Returns:
        set: Set of unique domains extracted from web sources
    """
    # Initialize set to store domains from web sources
    unique_domains = set()
    
    # Process each URL in the list
    for url in urls:
        logging.info(f"Processing URL: {url}")
        # Download content from the URL
        content = get_raw_content(url)
        
        if content:
            domain_count = 0
            # Process each line of the downloaded content
            for line in content.splitlines():
                # Extract domain from the line using regex pattern
                domain = process_line(line, domain_pattern)
                if domain:
                    # Add www. prefix and add to unique domains set
                    unique_domains.add(f"www.{domain}")
                    domain_count += 1
            
            logging.info(f"  - Extracted {domain_count} domains from {url}")
        else:
            # Log warning if no content was retrieved
            logging.warning(f"  - No content retrieved from {url}")
    
    return unique_domains

def create_formatted_domains_file(input_directory, urls, output_file, whitelist_file, custom_blocklist_file=None):
    """
    Create the main formatted_domains.txt file with comprehensive domain processing.
    
    This is the core function that combines domains from all sources (local files,
    web sources, custom blocklists), applies whitelist filtering, and creates the
    main output file with domains in www.domain.com format.
    
    Args:
        input_directory (str): Directory containing local blocklist files
        urls (list): List of URLs to download blocklists from
        output_file (str): Path where the final blocklist will be saved
        whitelist_file (str): Path to the whitelist file
        custom_blocklist_file (str, optional): Path to custom blocklist file
        
    Returns:
        int: Number of unique blocked domains in the final list
    """
    logging.info("=== Creating formatted domains file ===")
    
    # Compile regex pattern to match domain names with optional protocol and www
    # This pattern captures the domain part without protocol or www prefix
    domain_pattern = re.compile(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    
    # Initialize set to store all unique domains from all sources
    all_domains = set()
    
    # Step 1: Process all local files in the input directory
    local_domains, processed_files = process_all_local_files(input_directory, domain_pattern)
    all_domains.update(local_domains)
    logging.info(f"Total domains from local files: {len(local_domains)}")
    
    # Log detailed statistics for each processed file
    logging.info("Processed local files:")
    for filename, line_count, domain_count in processed_files:
        logging.info(f"  - {filename}: {line_count} lines, {domain_count} domains")
    
    # Step 2: Process web-based blocklist sources
    web_domains = process_web_sources(urls, domain_pattern)
    all_domains.update(web_domains)
    logging.info(f"Total domains from web sources: {len(web_domains)}")
    
    # Step 3: Add custom blocklist domains if specified
    if custom_blocklist_file:
        custom_domains = load_custom_blocklist(custom_blocklist_file, domain_pattern)
        all_domains.update(custom_domains)
        logging.info(f"Total domains from custom blocklist: {len(custom_domains)}")
    
    # Step 4: Apply whitelist filtering to remove allowed domains
    whitelist = load_whitelist(whitelist_file)
    blocked_domains = all_domains - whitelist
    logging.info(f"Domains after whitelist filtering: {len(blocked_domains)} (removed {len(all_domains) - len(blocked_domains)})")
    
    # Step 5: Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Step 6: Write sorted domains to output file
    logging.info(f"Writing domains to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Sort domains alphabetically and write each on a new line
        for domain in sorted(blocked_domains):
            outfile.write(f"{domain}\n")
    
    logging.info(f"=== Formatted domains file created with {len(blocked_domains)} domains ===")
    return len(blocked_domains)

def remove_www_prefix(domain):
    """
    Remove the www. prefix from a domain name for sorted file format.
    
    This function standardizes domains for the sorted files by removing the
    www. prefix, creating the domain.com format used in alphabetically
    sorted output files.
    
    Args:
        domain (str): Domain name that may have www. prefix
        
    Returns:
        str: Domain name without www. prefix
    """
    # Check if domain starts with 'www.' (case-insensitive) and remove it
    return domain[4:] if domain.lower().startswith('www.') else domain

def get_first_alphanumeric(domain):
    """
    Get the first alphanumeric character from a domain for alphabetical sorting.
    
    This function determines which alphabetical file a domain should be placed in
    by finding the first letter or number in the domain name.
    
    Args:
        domain (str): Domain name to analyze
        
    Returns:
        str: First alphanumeric character (lowercase), or '0' as default
    """
    # Iterate through each character in the domain
    for char in domain:
        # Check if the character is alphanumeric (letter or digit)
        if char.isalnum():
            # Return lowercase version if it's a letter, otherwise return digit as-is
            return char.lower() if char.isalpha() else char
    
    # Default to '0' if no alphanumeric character is found
    return '0'

def create_sorted_domains_files(formatted_domains_file, output_dir):
    """
    Create alphabetically sorted domain files without www prefix.
    
    This function reads the main formatted domains file and creates separate
    files for each letter/number (0-9, a-z), with domains in domain.com format
    (without www. prefix). This provides organized access to domains by
    alphabetical categories.
    
    Args:
        formatted_domains_file (str): Path to the main formatted domains file
        output_dir (str): Directory where sorted files will be created
    """
    logging.info("=== Creating sorted domains files ===")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize domain collections for each alphanumeric character
    # string.digits = '0123456789', string.ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    domain_files = {char: [] for char in string.digits + string.ascii_lowercase}
    
    # Verify that the formatted domains file exists
    if not os.path.exists(formatted_domains_file):
        logging.error(f"Formatted domains file not found: {formatted_domains_file}")
        return
    
    # Read and categorize all domains from the formatted file
    logging.info(f"Reading domains from {formatted_domains_file}")
    total_domains = 0
    
    with open(formatted_domains_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            domain = line.strip()
            if domain:
                total_domains += 1
                # Remove www. prefix for sorted file format
                domain_without_www = remove_www_prefix(domain)
                # Determine which alphabetical category this domain belongs to
                first_char = get_first_alphanumeric(domain_without_www)
                # Add domain to the appropriate category
                domain_files[first_char].append(domain_without_www)
    
    logging.info(f"Processed {total_domains} domains for sorting")
    
    # Write sorted files for each alphabetical category
    total_written = 0
    for char in string.digits + string.ascii_lowercase:
        # Only create files for categories that have domains
        if domain_files[char]:
            # Create output file path for this category
            output_file = os.path.join(output_dir, f'{char}_domains.txt')
            
            with open(output_file, 'w', encoding='utf-8') as outfile:
                # Remove duplicates using set(), then sort alphabetically (case-insensitive)
                sorted_domains = sorted(set(domain_files[char]), key=str.lower)
                
                # Write each domain on a separate line
                for domain in sorted_domains:
                    outfile.write(f"{domain}\n")
                    total_written += 1
            
            logging.info(f"Created {output_file} with {len(sorted_domains)} domains")
    
    logging.info(f"=== Sorted domains files created with {total_written} total domains ===")

def verify_brennans_domains_inclusion(formatted_domains_file):
    """
    Verify that domains from brennans_domains.txt are included in the final output.
    
    This function performs a verification check to ensure that the specific
    domains from brennans_domains.txt are properly included in the final
    formatted domains file, helping to identify any processing issues.
    
    Args:
        formatted_domains_file (str): Path to the final formatted domains file
    """
    logging.info("=== Verifying brennans_domains.txt inclusion ===")
    
    # Define path to the brennans domains file
    brennans_file = 'block_list_files/brennans_domains.txt'
    
    # Check if the brennans domains file exists
    if not os.path.exists(brennans_file):
        logging.warning(f"brennans_domains.txt not found at {brennans_file}")
        return
    
    # Read all domains from brennans_domains.txt
    brennans_domains = set()
    with open(brennans_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            domain = line.strip()
            # Skip empty lines and comments
            if domain and not domain.startswith('#'):
                brennans_domains.add(domain)
    
    logging.info(f"Found {len(brennans_domains)} domains in brennans_domains.txt")
    
    # Read all domains from the formatted domains file
    formatted_domains = set()
    with open(formatted_domains_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            domain = line.strip()
            if domain:
                formatted_domains.add(domain)
    
    # Check for any missing domains
    missing_domains = brennans_domains - formatted_domains
    
    if missing_domains:
        # Log warning about missing domains
        logging.warning(f"Missing {len(missing_domains)} domains from brennans_domains.txt:")
        # Show first 10 missing domains
        for domain in sorted(list(missing_domains)[:10]):
            logging.warning(f"  - {domain}")
        if len(missing_domains) > 10:
            logging.warning(f"  ... and {len(missing_domains) - 10} more")
    else:
        # All domains are included - success!
        logging.info("✓ All domains from brennans_domains.txt are included in formatted_domains.txt")

def main():
    """
    Main processing function that orchestrates the entire blocklist creation process.
    
    This function coordinates all the steps needed to create comprehensive blocklists:
    1. Processing local and web sources
    2. Creating the main formatted domains file
    3. Creating alphabetically sorted domain files
    4. Verifying specific file inclusion
    5. Providing comprehensive logging and error handling
    """
    logging.info("Starting comprehensive block list processing")
    
    # Configuration section - define all input sources and output locations
    input_directory = './block_list_files'  # Directory containing local blocklist files
    
    # List of web-based blocklist sources to download and process
    urls = [
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/multi.txt",
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/doh-vpn-proxy-bypass-onlydomains.txt",
        "https://github.com/sjhgvr/oisd/blob/main/domainswild2_nsfw_small.txt"
    ]
    
    # Output file locations
    formatted_output_file = 'combined_single_files/formatted_domains.txt'  # Main output with www. prefix
    sorted_output_dir = 'sorted_domains'                                   # Directory for alphabetical files
    
    # Configuration files
    whitelist_file = 'whitelist_files/whitelist.txt'                      # Domains to exclude from blocking
    custom_blocklist_file = 'block_list_files/add_extra_domains.txt'      # Additional domains to block
    
    try:
        # Step 1: Create the main formatted domains file (www.domain.com format)
        total_domains = create_formatted_domains_file(
            input_directory, urls, formatted_output_file, 
            whitelist_file, custom_blocklist_file
        )
        
        # Step 2: Create alphabetically sorted domain files (domain.com format)
        create_sorted_domains_files(formatted_output_file, sorted_output_dir)
        
        # Step 3: Verify that brennans_domains.txt domains are included
        verify_brennans_domains_inclusion(formatted_output_file)
        
        # Final success reporting
        logging.info(f"=== PROCESSING COMPLETE ===")
        logging.info(f"Total unique domains processed: {total_domains}")
        logging.info(f"Formatted domains file: {formatted_output_file}")
        logging.info(f"Sorted domains directory: {sorted_output_dir}")
        
    except Exception as e:
        # Log any critical errors that occur during processing
        logging.error(f"Error during processing: {e}")
        # Re-raise the exception to ensure the script exits with an error code
        raise

# Main execution block - only runs when script is executed directly (not imported)
if __name__ == "__main__":
    main() 