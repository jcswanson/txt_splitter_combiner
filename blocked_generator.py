# Import the os module for operating system interface functions (file/directory operations)
import os

def combine_files(input_files, output_file):
    """
    Combine multiple text files into a single output file with text processing.
    
    This function reads from multiple input files and writes to a single output file,
    removing the first 8 characters from each line (typically used to remove prefixes
    like "0.0.0.0 " from host file entries).
    
    Args:
        input_files (list): List of file paths to read from
        output_file (str): Path to the output file where combined content will be written
    """
    # Open the output file in write mode
    with open(output_file, 'w') as outfile:
        # Iterate through each input file in the list
        for file in input_files:
            # Open each input file in read mode
            with open(file, 'r') as infile:
                # Process each line in the current input file
                for line in infile:
                    # Remove the first 8 characters from the line (e.g., "0.0.0.0 " prefix)
                    # Note: Comment says 10 characters but code removes 8
                    stripped_line = line[8:]  # remove the first 8 characters
                    # Write the processed line to the output file
                    outfile.write(stripped_line)

# Main execution block - only runs when script is executed directly (not imported)
if __name__ == "__main__":
    # Specify the directory where the input text files are located
    input_dir = 'block_list_files'
    
    # Get a list of all .txt files in the input directory
    # os.path.join() creates proper file paths, os.listdir() lists directory contents
    # List comprehension filters only files ending with '.txt'
    input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    # Specify the name of the output file where combined content will be saved
    output_file = 'combined_block_list.txt'
    
    # Call the function to combine all the files
    combine_files(input_files, output_file)