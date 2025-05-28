# Block List Generator

A comprehensive Python-based system for creating and managing domain blocklists from multiple sources. This tool combines local blocklist files with web-based sources to generate organized, deduplicated domain blocklists in multiple formats.

## 🚀 Features

- **Multi-source processing**: Combines local files and web-based blocklists
- **Dual output formats**: 
  - `www.domain.com` format for main blocklist
  - `domain.com` format for alphabetically sorted files
- **Whitelist filtering**: Excludes allowed domains from blocking
- **Automatic deduplication**: Removes duplicate entries across all sources
- **Alphabetical organization**: Creates separate files for each letter/number (0-9, a-z)
- **Comprehensive logging**: Detailed processing logs and verification
- **Error handling**: Robust processing with graceful error recovery

## 📁 Project Structure

```
block_list_gen/
├── block_list_files/           # Input directory for local blocklist files
│   ├── brennans_domains.txt    # Brennan's domain list
│   ├── add_extra_domains.txt   # Any added domains to block
│   ├── Adult.txt              # Adult content domains
│   ├── black-list.txt         # General blocklist
│   └── *.txt                  # Any other .txt blocklist files
├── combined_single_files/      # Output directory for main blocklist
│   └── formatted_domains.txt  # Main output (www.domain.com format for Taieb's system list)
├── sorted_domains/            # Output directory for alphabetical files for Sleke Links
│   ├── 0_domains.txt         # Domains starting with numbers
│   ├── a_domains.txt         # Domains starting with 'a'
│   └── ...                   # Files for each letter/number
├── whitelist_files/          # Whitelist configuration
│   └── whitelist.txt         # Domains to exclude from blocking
└── *.py                      # Python scripts (detailed below)
```

## 🐍 Python Scripts Overview

### 1. `comprehensive_block_list_processor.py` ⭐ **RECOMMENDED**

**The main script that replaces all others** - provides complete blocklist processing with all features.

#### What it does:
- Processes ALL `.txt` files in `block_list_files/` directory
- Downloads and processes web-based blocklists
- Applies whitelist filtering
- Creates `formatted_domains.txt` with `www.domain.com` format
- Creates alphabetically sorted files with `domain.com` format
- Provides comprehensive logging and verification

#### Usage:
```bash
python comprehensive_block_list_processor.py
```

#### Output:
- `combined_single_files/formatted_domains.txt` - Main blocklist (2.5M+ domains)
- `sorted_domains/*.txt` - 36 alphabetically sorted files
- `block_list_processing.log` - Detailed processing log

---

### 2. `main_www_block_list_gen_.py`

**Legacy script** for creating the main formatted domains file (now superseded by comprehensive processor).

#### What it does:
- Processes local files and web sources
- Creates formatted domains with `www.` prefix
- Applies whitelist filtering
- Includes custom blocklist support

#### Usage:
```bash
python main_www_block_list_gen_.py
```

---

### 3. `sleke_links_strip_and_sort_dir_gen.py`

**Domain sorting script** that creates alphabetically organized files.

#### What it does:
- Reads `formatted_domains.txt`
- Removes `www.` prefixes
- Sorts domains into alphabetical files (0-9, a-z)
- Provides detailed logging

#### Usage:
```bash
python sleke_links_strip_and_sort_dir_gen.py
```

#### Functions:
- `get_first_alphanumeric(domain)` - Finds first letter/number for sorting
- `remove_www(domain)` - Removes www. prefix
- `sort_domains(file_name)` - Main sorting function

---

### 4. `domain_splitter.py`

**Alternative domain organizer** that processes files directly from `block_list_files/`.

#### What it does:
- Processes all `.txt` files in `block_list_files/`
- Removes `www.` prefixes
- Creates alphabetically sorted files in `sorted-black-domains/`
- Uses sets for automatic deduplication

#### Usage:
```bash
python domain_splitter.py
```

---

### 5. `blocked_generator.py`

**Simple file combiner** that merges multiple text files with prefix removal.

#### What it does:
- Combines all `.txt` files from `block_list_files/`
- Removes first 8 characters from each line (e.g., "0.0.0.0 " prefix)
- Creates `combined_block_list.txt`

#### Usage:
```bash
python blocked_generator.py
```

#### Functions:
- `combine_files(input_files, output_file)` - Combines files with text processing

## 🔧 Setup and Installation

### Prerequisites
- Python 3.6 or higher
- Required packages: `requests`

### Installation
1. Clone or download the repository
2. Install required packages:
   ```bash
   pip install requests
   ```
3. Ensure directory structure exists:
   ```bash
   mkdir -p block_list_files combined_single_files sorted_domains whitelist_files
   ```

## 📖 Usage Guide

### Quick Start (Recommended)
```bash
# Run the comprehensive processor (does everything)
python comprehensive_block_list_processor.py
```

### Step-by-Step Process
If you prefer to run individual scripts:

1. **Create main blocklist:**
   ```bash
   python main_www_block_list_gen_.py
   ```

2. **Create sorted files:**
   ```bash
   python sleke_links_strip_and_sort_dir_gen.py
   ```

### Adding Custom Domains
1. Add domains to `block_list_files/add_extra_domains.txt` (one per line)
2. Add any `.txt` file to `block_list_files/` directory
3. Run the comprehensive processor

### Whitelisting Domains
1. Add domains to `whitelist_files/whitelist.txt` (one per line, without www.)
2. These domains will be excluded from all blocklists

## 📊 Output Formats

### Main Blocklist (`formatted_domains.txt`)
```
www.example.com
www.badsite.org
www.malware.net
```

### Sorted Files (`a_domains.txt`, `b_domains.txt`, etc.)
```
example.com
badsite.org
malware.net
```

## 🔍 Web Sources

The scripts automatically downloads from these online sources:
- **Hagezi Multi-domain blocklist**: Comprehensive domain blocking
- **Hagezi DoH/VPN/Proxy bypass**: Blocks DNS-over-HTTPS and proxy domains
- **OISD NSFW domains**: Adult content blocking

## 📝 Logging

All scripts provide detailed logging:
- **Console output**: Real-time processing information
- **Log files**: Permanent record of processing (where applicable)
- **Statistics**: Domain counts, file processing stats, error reports

## 🛠️ Troubleshooting

### Common Issues

1. **"File not found" errors**
   - Ensure all required directories exist
   - Check file paths in scripts

2. **Network errors**
   - Check internet connection for web source downloads
   - Verify URLs are accessible

3. **Memory issues with large files**
   - Large blocklists may require sufficient RAM
   - Consider processing smaller batches

4. **Encoding errors**
   - Scripts use UTF-8 encoding with error handling
   - Check source file encodings if issues persist

### Debug Mode
Enable detailed logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## 📈 Performance

- **Processing time**: 2-5 minutes for full processing
- **Output size**: ~72MB main file, ~50MB sorted files
- **Domain count**: 2.5M+ unique domains
- **Memory usage**: ~500MB peak during processing

## 🤝 Adding Functions

1. Add new blocklist sources to the `urls` list in `comprehensive_block_list_processor.py`
2. Modify domain processing logic in `process_line()` function
3. Add new output formats by extending the processing functions

---

**Note**: The `comprehensive_block_list_processor.py` script is the recommended approach as it provides all functionality in a single, well-tested script with comprehensive error handling and logging. 