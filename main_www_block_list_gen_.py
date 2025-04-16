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


def load_custom_blocklist(custom_blocklist_file, domain_pattern):
    custom_domains = set()
    if os.path.exists(custom_blocklist_file):
        with open(custom_blocklist_file, 'r', encoding='utf-8') as cfile:
            for line in cfile:
                domain = process_line(line, domain_pattern)
                if domain:
                    custom_domains.add(f"www.{domain}")
                else:
                    # If process_line doesn't extract a domain, try to use the line directly
                    clean_domain = line.strip()
                    if clean_domain and not clean_domain.startswith('#'):
                        if not clean_domain.startswith('www.'):
                            clean_domain = f"www.{clean_domain}"
                        custom_domains.add(clean_domain)
    return custom_domains


def process_domains(input_directory, urls, output_file, whitelist_file, custom_blocklist_file=None):
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

    # Add custom blocklist domains if provided
    if custom_blocklist_file:
        print(f"Processing custom blocklist: {custom_blocklist_file}")
        custom_domains = load_custom_blocklist(custom_blocklist_file, domain_pattern)
        unique_domains.update(custom_domains)

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
        "https://github.com/sjhgvr/oisd/blob/main/domainswild2_nsfw_small.txt"
    ]
    output_file = 'combined_single_files/formatted_domains.txt'
    whitelist_file = 'whitelist_files/whitelist.txt'
    custom_blocklist_file = 'block_list_files/add_extra_domains.txt'  # New parameter for custom blocklist

    total_domains = process_domains(input_directory, urls, output_file, whitelist_file, custom_blocklist_file)
    print(f"Processing complete. {total_domains} unique domains saved to {output_file}")
    print("Done.")
