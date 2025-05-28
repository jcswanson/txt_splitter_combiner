# Import necessary modules for regex operations, file system operations, and web requests
import re
import os
import requests
from urllib.parse import urlparse


def is_github_url(url):
    """
    Check if a given URL is from GitHub (either github.com or raw.githubusercontent.com)
    
    Args:
        url (str): The URL to check
        
    Returns:
        bool: True if the URL is from GitHub, False otherwise
    """
    # Parse the URL to extract its components (scheme, netloc, path, etc.)
    parsed_url = urlparse(url)
    # Check if the network location (domain) is either github.com or raw.githubusercontent.com
    return parsed_url.netloc == "github.com" or parsed_url.netloc == "raw.githubusercontent.com"


def get_raw_content(url):
    """
    Download raw content from a URL, converting GitHub URLs to raw format if needed
    
    Args:
        url (str): The URL to download content from
        
    Returns:
        str: The raw text content from the URL
    """
    # If it's a GitHub URL but not already in raw format, convert it
    if is_github_url(url) and "raw" not in url:
        # Replace github.com with raw.githubusercontent.com to get raw file content
        url = url.replace("github.com", "raw.githubusercontent.com")
        # Remove /blob/ from the path as it's not needed for raw content
        url = url.replace("/blob/", "/")
    # Make HTTP GET request to download the content
    response = requests.get(url)
    # Return the text content of the response
    return response.text


def process_line(line, domain_pattern):
    """
    Extract a domain from a line of text using regex pattern matching
    
    Args:
        line (str): A line of text that may contain a domain
        domain_pattern (re.Pattern): Compiled regex pattern to match domains
        
    Returns:
        str or None: The extracted domain if found, None otherwise
    """
    # Skip comment lines (starting with #) and empty lines
    if line.strip().startswith('#') or not line.strip():
        return None
    
    # Split the line into parts (handles formats like "0.0.0.0 domain.com")
    parts = line.strip().split()
    if not parts:
        return None
    
    # Take the last part (usually the domain in blocklist formats)
    line = parts[-1]
    
    # Use regex to search for a valid domain pattern in the line
    match = domain_pattern.search(line)
    if match:
        # Return the first captured group (the domain without protocol/www)
        return match.group(1)
    return None


def load_whitelist(whitelist_file):
    """
    Load domains from a whitelist file into a set for fast lookup
    
    Args:
        whitelist_file (str): Path to the whitelist file
        
    Returns:
        set: Set of whitelisted domains with www. prefix
    """
    # Initialize empty set to store whitelisted domains
    whitelist = set()
    
    # Check if the whitelist file exists before trying to read it
    if os.path.exists(whitelist_file):
        # Open the file with UTF-8 encoding
        with open(whitelist_file, 'r', encoding='utf-8') as wfile:
            # Process each line in the whitelist file
            for line in wfile:
                # Remove whitespace and get the domain
                domain = line.strip()
                if domain:
                    # Add www. prefix and add to whitelist set
                    whitelist.add(f"www.{domain}")
    return whitelist


def load_custom_blocklist(custom_blocklist_file, domain_pattern):
    """
    Load additional domains from a custom blocklist file
    
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
                    # If process_line doesn't extract a domain, try to use the line directly
                    clean_domain = line.strip()
                    # Skip empty lines and comments
                    if clean_domain and not clean_domain.startswith('#'):
                        # Add www. prefix if not already present
                        if not clean_domain.startswith('www.'):
                            clean_domain = f"www.{clean_domain}"
                        custom_domains.add(clean_domain)
    return custom_domains


def process_domains(input_directory, urls, output_file, whitelist_file, custom_blocklist_file=None):
    """
    Main processing function that combines domains from multiple sources and creates filtered blocklist
    
    Args:
        input_directory (str): Directory containing local blocklist files
        urls (list): List of URLs to download blocklists from
        output_file (str): Path where the final blocklist will be saved
        whitelist_file (str): Path to the whitelist file
        custom_blocklist_file (str, optional): Path to custom blocklist file
        
    Returns:
        int: Number of unique blocked domains in the final list
    """
    # Compile regex pattern to match domain names (with optional protocol and www)
    domain_pattern = re.compile(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    
    # Initialize set to store all unique domains
    unique_domains = set()
    
    # Load the whitelist domains
    whitelist = load_whitelist(whitelist_file)

    # Process local files in the input directory
    for filename in os.listdir(input_directory):
        # Only process text files
        if filename.endswith('.txt'):
            # Create full path to the input file
            input_file = os.path.join(input_directory, filename)
            print(f"Processing file: {input_file}")
            
            # Open file with UTF-8 encoding and ignore encoding errors
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
                # Process each line in the file
                for line in infile:
                    # Extract domain from the line
                    domain = process_line(line, domain_pattern)
                    if domain:
                        # Add www. prefix and add to unique domains set
                        unique_domains.add(f"www.{domain}")

    # Process web sources (download and extract domains)
    for url in urls:
        print(f"Processing URL: {url}")
        # Download content from the URL
        content = get_raw_content(url)
        # Process each line of the downloaded content
        for line in content.splitlines():
            # Extract domain from the line
            domain = process_line(line, domain_pattern)
            if domain:
                # Add www. prefix and add to unique domains set
                unique_domains.add(f"www.{domain}")

    # Add custom blocklist domains if a custom file is provided
    if custom_blocklist_file:
        print(f"Processing custom blocklist: {custom_blocklist_file}")
        # Load domains from custom blocklist
        custom_domains = load_custom_blocklist(custom_blocklist_file, domain_pattern)
        # Add all custom domains to the main set
        unique_domains.update(custom_domains)

    # Remove whitelisted domains from the blocked domains
    blocked_domains = unique_domains - whitelist

    # Write the final sorted list of blocked domains to output file
    with open(output_file, 'w') as outfile:
        # Sort domains alphabetically and write each on a new line
        for domain in sorted(blocked_domains):
            outfile.write(f"{domain}\n")

    # Return the total count of blocked domains
    return len(blocked_domains)


# Main execution block - only runs when script is executed directly (not imported)
if __name__ == "__main__":
    # Define the directory containing local blocklist files
    input_directory = './block_list_files'
    
    # Define list of URLs to download blocklists from
    urls = [
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/multi.txt",
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/doh-vpn-proxy-bypass-onlydomains.txt",
        "https://github.com/sjhgvr/oisd/blob/main/domainswild2_nsfw_small.txt"
    ]
    
    # Define output file path for the final combined blocklist
    output_file = 'combined_single_files/formatted_domains.txt'
    
    # Define path to the whitelist file (domains to exclude from blocking)
    whitelist_file = 'whitelist_files/whitelist.txt'
    
    # Define path to custom blocklist file (additional domains to block)
    custom_blocklist_file = 'block_list_files/add_extra_domains.txt'

    # Execute the main processing function with all parameters
    total_domains = process_domains(input_directory, urls, output_file, whitelist_file, custom_blocklist_file)
    
    # Print completion message with total count
    print(f"Processing complete. {total_domains} unique domains saved to {output_file}")
    print("Done.")
