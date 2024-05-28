import re

def remove_http_www_trailing_slash(domain):
    domain = re.sub('http://', '', domain)
    domain = re.sub('https://', '', domain)
    domain = re.sub('www.', '', domain)
    domain = domain.rstrip('/')
    return domain

def sort_domains(domains):
    sorted_domains = sorted(set(domains), key=lambda x: remove_http_www_trailing_slash(x))
    return sorted_domains

def process_file(file_name):
    with open(file_name, 'r') as file:
        domains = file.readlines()
        domains = [domain.strip() for domain in domains]
        domains = list(filter(None, domains))
        domains = [remove_http_www_trailing_slash(domain) for domain in domains]
        sorted_domains = sort_domains(domains)
        return sorted_domains

file_name = "./block_list_files/brennans-list.txt"
sorted_domains = process_file(file_name)
for domain in sorted_domains:
    print(domain)