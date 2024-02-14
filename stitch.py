import os
import argparse

def stitch_files(directory, output_file, base_filename):
    """
    Stitch together file parts into a single file.

    :param directory: Directory where the file parts are stored.
    :param output_file: The name of the output file to create.
    :param base_filename: The base name of the file parts to stitch together.
    """
    # Ensure the directory ends with a slash
    if not directory.endswith(os.path.sep):
        directory += os.path.sep

    # Initialize a list to hold the file parts
    parts = []

    # List all files in the directory and filter out the parts
    for filename in os.listdir(directory):
        if filename.startswith(base_filename) and filename != output_file:
            parts.append(filename)

    # Sort the parts by their part number
    parts.sort(key=lambda x: int(x.split('part')[-1]))

    # Open the output file in write-binary mode
    with open(directory + output_file, 'wb') as output:
        # Iterate over each part and append its contents to the output file
        for part in parts:
            with open(directory + part, 'rb') as f:
                output.write(f.read())

    print(f"Stitched {len(parts)} parts into {output_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Stitch file parts together")
    parser.add_argument("base_filename", help="The base filename for the parts to stitch")
    parser.add_argument("-d", "--directory", default=".", help="Directory where the file parts are stored (default is current directory)")
    parser.add_argument("-o", "--output_file", default="stitched_output.file", help="Name of the output file (default is 'stitched_output.file')")

    args = parser.parse_args()

    # Call the function with command-line arguments
    stitch_files(args.directory, args.output_file, args.base_filename)
