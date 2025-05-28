#!/usr/bin/env python3
"""
Comprehensive Block List Processor

This script ensures:
1. All files in block_list_files directory are included
2. formatted_domains.txt contains domains in 'www.domain.com' format
3. sorted_domains files contain domains in 'domain.com' format
4. Proper deduplication and sorting
5. Comprehensive logging and verification
"""

import os
import re
import requests
import string
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('block_list_processing.log'),
        logging.StreamHandler()
    ]
)

def is_github_url(url):
    """Check if a given URL is from GitHub"""
    parsed_url = urlparse(url)
    return parsed_url.netloc == "github.com" or parsed_url.netloc == "raw.githubusercontent.com"

def get_raw_content(url):
    """Download raw content from a URL, converting GitHub URLs to raw format if needed"""
    if is_github_url(url) and "raw" not in url:
        url = url.replace("github.com", "raw.githubusercontent.com")
        url = url.replace("/blob/", "/")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
        return ""

def process_line(line, domain_pattern):
    """Extract a domain from a line of text using regex pattern matching"""
    if line.strip().startswith('#') or not line.strip():
        return None
    
    parts = line.strip().split()
    if not parts:
        return None
    
    line = parts[-1]
    match = domain_pattern.search(line)
    if match:
        return match.group(1)
    return None

def load_whitelist(whitelist_file):
    """Load domains from a whitelist file into a set for fast lookup"""
    whitelist = set()
    if os.path.exists(whitelist_file):
        logging.info(f"Loading whitelist from {whitelist_file}")
        with open(whitelist_file, 'r', encoding='utf-8') as wfile:
            for line in wfile:
                domain = line.strip()
                if domain:
                    whitelist.add(f"www.{domain}")
        logging.info(f"Loaded {len(whitelist)} whitelisted domains")
    else:
        logging.warning(f"Whitelist file not found: {whitelist_file}")
    return whitelist

def load_custom_blocklist(custom_blocklist_file, domain_pattern):
    """Load additional domains from a custom blocklist file"""
    custom_domains = set()
    if os.path.exists(custom_blocklist_file):
        logging.info(f"Loading custom blocklist from {custom_blocklist_file}")
        with open(custom_blocklist_file, 'r', encoding='utf-8') as cfile:
            for line in cfile:
                domain = process_line(line, domain_pattern)
                if domain:
                    custom_domains.add(f"www.{domain}")
                else:
                    clean_domain = line.strip()
                    if clean_domain and not clean_domain.startswith('#'):
                        if not clean_domain.startswith('www.'):
                            clean_domain = f"www.{clean_domain}"
                        custom_domains.add(clean_domain)
        logging.info(f"Loaded {len(custom_domains)} custom domains")
    else:
        logging.warning(f"Custom blocklist file not found: {custom_blocklist_file}")
    return custom_domains

def process_all_local_files(input_directory, domain_pattern):
    """Process ALL .txt files in the input directory"""
    unique_domains = set()
    processed_files = []
    
    if not os.path.exists(input_directory):
        logging.error(f"Input directory not found: {input_directory}")
        return unique_domains, processed_files
    
    # Get all .txt files in the directory
    txt_files = [f for f in os.listdir(input_directory) if f.endswith('.txt')]
    logging.info(f"Found {len(txt_files)} .txt files in {input_directory}")
    
    for filename in txt_files:
        input_file = os.path.join(input_directory, filename)
        logging.info(f"Processing file: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
                line_count = 0
                domain_count = 0
                for line in infile:
                    line_count += 1
                    domain = process_line(line, domain_pattern)
                    if domain:
                        unique_domains.add(f"www.{domain}")
                        domain_count += 1
                
                logging.info(f"  - Processed {line_count} lines, extracted {domain_count} domains")
                processed_files.append((filename, line_count, domain_count))
                
        except Exception as e:
            logging.error(f"Error processing {input_file}: {e}")
    
    return unique_domains, processed_files

def process_web_sources(urls, domain_pattern):
    """Process web sources and extract domains"""
    unique_domains = set()
    
    for url in urls:
        logging.info(f"Processing URL: {url}")
        content = get_raw_content(url)
        if content:
            domain_count = 0
            for line in content.splitlines():
                domain = process_line(line, domain_pattern)
                if domain:
                    unique_domains.add(f"www.{domain}")
                    domain_count += 1
            logging.info(f"  - Extracted {domain_count} domains from {url}")
        else:
            logging.warning(f"  - No content retrieved from {url}")
    
    return unique_domains

def create_formatted_domains_file(input_directory, urls, output_file, whitelist_file, custom_blocklist_file=None):
    """Create the main formatted_domains.txt file with www.domain.com format"""
    logging.info("=== Creating formatted domains file ===")
    
    domain_pattern = re.compile(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    all_domains = set()
    
    # Process local files
    local_domains, processed_files = process_all_local_files(input_directory, domain_pattern)
    all_domains.update(local_domains)
    logging.info(f"Total domains from local files: {len(local_domains)}")
    
    # Log processed files
    logging.info("Processed local files:")
    for filename, line_count, domain_count in processed_files:
        logging.info(f"  - {filename}: {line_count} lines, {domain_count} domains")
    
    # Process web sources
    web_domains = process_web_sources(urls, domain_pattern)
    all_domains.update(web_domains)
    logging.info(f"Total domains from web sources: {len(web_domains)}")
    
    # Add custom blocklist domains
    if custom_blocklist_file:
        custom_domains = load_custom_blocklist(custom_blocklist_file, domain_pattern)
        all_domains.update(custom_domains)
        logging.info(f"Total domains from custom blocklist: {len(custom_domains)}")
    
    # Load whitelist and filter
    whitelist = load_whitelist(whitelist_file)
    blocked_domains = all_domains - whitelist
    logging.info(f"Domains after whitelist filtering: {len(blocked_domains)} (removed {len(all_domains) - len(blocked_domains)})")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write domains to output file
    logging.info(f"Writing domains to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for domain in sorted(blocked_domains):
            outfile.write(f"{domain}\n")
    
    logging.info(f"=== Formatted domains file created with {len(blocked_domains)} domains ===")
    return len(blocked_domains)

def remove_www_prefix(domain):
    """Remove www. prefix from domain"""
    return domain[4:] if domain.lower().startswith('www.') else domain

def get_first_alphanumeric(domain):
    """Get the first alphanumeric character from domain"""
    for char in domain:
        if char.isalnum():
            return char.lower() if char.isalpha() else char
    return '0'  # Default to '0' if no alphanumeric character is found

def create_sorted_domains_files(formatted_domains_file, output_dir):
    """Create alphabetically sorted domain files without www prefix"""
    logging.info("=== Creating sorted domains files ===")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize domain collections
    domain_files = {char: [] for char in string.digits + string.ascii_lowercase}
    
    if not os.path.exists(formatted_domains_file):
        logging.error(f"Formatted domains file not found: {formatted_domains_file}")
        return
    
    # Read and process domains
    logging.info(f"Reading domains from {formatted_domains_file}")
    total_domains = 0
    with open(formatted_domains_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            domain = line.strip()
            if domain:
                total_domains += 1
                # Remove www. prefix
                domain_without_www = remove_www_prefix(domain)
                # Get first character for sorting
                first_char = get_first_alphanumeric(domain_without_www)
                domain_files[first_char].append(domain_without_www)
    
    logging.info(f"Processed {total_domains} domains for sorting")
    
    # Write sorted files
    total_written = 0
    for char in string.digits + string.ascii_lowercase:
        if domain_files[char]:
            output_file = os.path.join(output_dir, f'{char}_domains.txt')
            with open(output_file, 'w', encoding='utf-8') as outfile:
                sorted_domains = sorted(set(domain_files[char]), key=str.lower)  # Remove duplicates and sort
                for domain in sorted_domains:
                    outfile.write(f"{domain}\n")
                    total_written += 1
            logging.info(f"Created {output_file} with {len(sorted_domains)} domains")
    
    logging.info(f"=== Sorted domains files created with {total_written} total domains ===")

def verify_brennans_domains_inclusion(formatted_domains_file):
    """Verify that domains from brennans_domains.txt are included in the final output"""
    logging.info("=== Verifying brennans_domains.txt inclusion ===")
    
    brennans_file = 'block_list_files/brennans_domains.txt'
    if not os.path.exists(brennans_file):
        logging.warning(f"brennans_domains.txt not found at {brennans_file}")
        return
    
    # Read brennans domains
    brennans_domains = set()
    with open(brennans_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            domain = line.strip()
            if domain and not domain.startswith('#'):
                brennans_domains.add(domain)
    
    logging.info(f"Found {len(brennans_domains)} domains in brennans_domains.txt")
    
    # Read formatted domains
    formatted_domains = set()
    with open(formatted_domains_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            domain = line.strip()
            if domain:
                formatted_domains.add(domain)
    
    # Check inclusion
    missing_domains = brennans_domains - formatted_domains
    if missing_domains:
        logging.warning(f"Missing {len(missing_domains)} domains from brennans_domains.txt:")
        for domain in sorted(list(missing_domains)[:10]):  # Show first 10
            logging.warning(f"  - {domain}")
        if len(missing_domains) > 10:
            logging.warning(f"  ... and {len(missing_domains) - 10} more")
    else:
        logging.info("✓ All domains from brennans_domains.txt are included in formatted_domains.txt")

def main():
    """Main processing function"""
    logging.info("Starting comprehensive block list processing")
    
    # Configuration
    input_directory = './block_list_files'
    urls = [
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/multi.txt",
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/doh-vpn-proxy-bypass-onlydomains.txt",
        "https://github.com/sjhgvr/oisd/blob/main/domainswild2_nsfw_small.txt"
    ]
    formatted_output_file = 'combined_single_files/formatted_domains.txt'
    sorted_output_dir = 'sorted_domains'
    whitelist_file = 'whitelist_files/whitelist.txt'
    custom_blocklist_file = 'block_list_files/add_extra_domains.txt'
    
    try:
        # Step 1: Create formatted domains file (www.domain.com format)
        total_domains = create_formatted_domains_file(
            input_directory, urls, formatted_output_file, 
            whitelist_file, custom_blocklist_file
        )
        
        # Step 2: Create sorted domains files (domain.com format)
        create_sorted_domains_files(formatted_output_file, sorted_output_dir)
        
        # Step 3: Verify brennans_domains.txt inclusion
        verify_brennans_domains_inclusion(formatted_output_file)
        
        logging.info(f"=== PROCESSING COMPLETE ===")
        logging.info(f"Total unique domains processed: {total_domains}")
        logging.info(f"Formatted domains file: {formatted_output_file}")
        logging.info(f"Sorted domains directory: {sorted_output_dir}")
        
    except Exception as e:
        logging.error(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    main() 