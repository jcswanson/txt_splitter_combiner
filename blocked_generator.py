import os

def combine_files(input_files, output_file):
    with open(output_file, 'w') as outfile:
        for file in input_files:
            with open(file, 'r') as infile:
                for line in infile:
                    stripped_line = line[8:]  # remove the first 10 characters
                    outfile.write(stripped_line)

if __name__ == "__main__":
    # specify the directory where the text files are located
    input_dir = './block_files'
    # get a list of all the text files in the directory
    input_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    # specify the output file name
    output_file = 'combined_block_list.txt'
    # call the function to combine the files
    combine_files(input_files, output_file)