import re
import os
import requests
from urllib.parse import urlparse

def is_github_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc == "github.com" or parsed_url.netloc == "raw.githubusercontent.com"

def get_raw_content(url):
    if is_github_url(url) and "raw" not in url:
        url = url.replace("github.com", "raw.githubusercontent.com")
        url = url.replace("/blob/", "/")
    response = requests.get(url)
    return response.text

def process_line(line, domain_pattern):
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
    whitelist = set()
    if os.path.exists(whitelist_file):
        with open(whitelist_file, 'r', encoding='utf-8') as wfile:
            for line in wfile:
                domain = line.strip()
                if domain:
                    whitelist.add(f"www.{domain}")
    return whitelist

def process_domains(input_directory, urls, output_file, whitelist_file):
    domain_pattern = re.compile(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
    unique_domains = set()
    whitelist = load_whitelist(whitelist_file)

    # Process local files
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            input_file = os.path.join(input_directory, filename)
            print(f"Processing file: {input_file}")
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
                for line in infile:
                    domain = process_line(line, domain_pattern)
                    if domain:
                        unique_domains.add(f"www.{domain}")

    # Process web sources
    for url in urls:
        print(f"Processing URL: {url}")
        content = get_raw_content(url)
        for line in content.splitlines():
            domain = process_line(line, domain_pattern)
            if domain:
                unique_domains.add(f"www.{domain}")

    # Remove whitelisted domains
    blocked_domains = unique_domains - whitelist

    # Write unique domains to output file
    with open(output_file, 'w') as outfile:
        for domain in sorted(blocked_domains):
            outfile.write(f"{domain}\n")

    return len(blocked_domains)

if __name__ == "__main__":
    input_directory = './block_list_files'
    urls = [
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/multi.txt",
        "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/doh-vpn-proxy-bypass-onlydomains.txt",
        "https://blocklistproject.github.io/Lists/everything.txt",
        "https://github.com/sjhgvr/oisd/blob/main/domainswild2_nsfw_small.txt"
    ]
    output_file = 'combined_single_files/formatted_domains.txt'
    whitelist_file = 'whitelist_files/whitelist.txt'  # Specify the path to your whitelist file

    total_domains = process_domains(input_directory, urls, output_file, whitelist_file)
    print(f"Processing complete. {total_domains} unique domains saved to {output_file}")
    print("Done.")