import os
import subprocess
import sys
import time

def download_resources():
    """Download necessary tools and files."""
    resources = [
        ("http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bigWigToBedGraph", "bigWigToBedGraph"),
        ("http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bedGraphToBigWig", "bedGraphToBigWig"),
        ("http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bedClip", "bedClip"),
        ("http://hgdownload.cse.ucsc.edu/goldenpath/hg19/liftOver/hg19ToHg38.over.chain.gz", "hg19ToHg38.over.chain.gz"),
        ("http://hgdownload.cse.ucsc.edu/goldenpath/hg38/liftOver/hg38ToHg19.over.chain.gz", "hg38ToHg19.over.chain.gz"),
        ("https://hgdownload.cse.ucsc.edu/goldenpath/hg38/bigZips/hg38.chrom.sizes", "hg38.chrom.sizes"),
        ("https://hgdownload.cse.ucsc.edu/goldenpath/hg19/bigZips/hg19.chrom.sizes", "hg19.chrom.sizes")
    ]
    for url, filename in resources:
        if not os.path.exists(filename):
            subprocess.run(["wget", url])
    
    # Make the UCSC tools executable
    for tool in ["bigWigToBedGraph", "bedGraphToBigWig", "bedClip"]:
        os.chmod(tool, 0o755)

def adjust_overlaps(input_file, output_file):
    """Adjust overlapping regions in a bedGraph file by slightly modifying end coordinates."""
    current_chrom = None
    current_end = 0

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            chrom, start, end, value = line.strip().split()
            start, end = int(start), int(end)

            if chrom != current_chrom:
                current_chrom = chrom
                current_end = 0

            if start < current_end:
                # Overlap detected, adjust the start
                start = current_end

            if start < end:  # Ensure the region is valid
                outfile.write(f"{chrom}\t{start}\t{end}\t{value}\n")
                current_end = end

def print_progress(step, total_steps, message):
    """Print a cool progress message."""
    progress = f"[{step}/{total_steps}]"
    sys.stdout.write(f"\r\033[K{progress} 🚀 {message}")
    sys.stdout.flush()
    time.sleep(0.5)  # Add a small delay for effect

def convert_bigwig(input_file, output_file, source_assembly, target_assembly, clean_temp=True):
    """
    Convert a bigWig file between hg19 and hg38, filtering non-standard chromosomes, 
    adjusting overlapping regions, and using bedClip.
    Args:
    input_file (str): Path to the input bigWig file
    output_file (str): Path to save the output bigWig file
    source_assembly (str): Source assembly ('hg19' or 'hg38')
    target_assembly (str): Target assembly ('hg19' or 'hg38')
    """
    if source_assembly not in ['hg19', 'hg38'] or target_assembly not in ['hg19', 'hg38']:
        raise ValueError("Source and target assemblies must be either 'hg19' or 'hg38'")
    if source_assembly == target_assembly:
        raise ValueError("Source and target assemblies must be different")

    total_steps = 9
    current_step = 1

    print_progress(current_step, total_steps, "Initializing genome conversion process...")
    current_step += 1

    # Ensure necessary resources are downloaded
    print_progress(current_step, total_steps, "Downloading resources...")
    download_resources()
    current_step += 1

    # Install CrossMap if not already installed
    print_progress(current_step, total_steps, "Installing CrossMap...")
    subprocess.run(["pip", "install", "CrossMap"])
    current_step += 1

    # Determine the chain file and chrom sizes file to use
    chain_file = f"{source_assembly}To{target_assembly.capitalize()}.over.chain.gz"
    chrom_sizes_file = f"{target_assembly}.chrom.sizes"

    # Load target chromosome sizes
    print_progress(current_step, total_steps, "Loading target chromosome sizes...")
    target_chroms = set()
    with open(chrom_sizes_file, 'r') as f:
        for line in f:
            chrom = line.strip().split()[0]
            target_chroms.add(chrom)
    current_step += 1

    # Convert bigWig to bedGraph
    print_progress(current_step, total_steps, "Converting bigWig to bedGraph...")
    subprocess.run(["./bigWigToBedGraph", input_file, "input.bedGraph"])
    current_step += 1

    # Use CrossMap to convert coordinates
    print_progress(current_step, total_steps, "Converting coordinates with CrossMap...")
    subprocess.run(["CrossMap", "bed", chain_file, "input.bedGraph", "output.bedGraph"])
    current_step += 1

    # Filter out non-standard chromosomes and use bedClip
    print_progress(current_step, total_steps, "Filtering chromosomes and clipping coordinates...")
    with open("output.bedGraph", 'r') as infile, open("filtered_output.bedGraph", 'w') as outfile:
        for line in infile:
            chrom = line.split()[0]
            if chrom in target_chroms:
                outfile.write(line)
    subprocess.run(["./bedClip", "filtered_output.bedGraph", chrom_sizes_file, "clipped_output.bedGraph"])
    subprocess.run("sort -k1,1 -k2,2n clipped_output.bedGraph > sorted_output.bedGraph", shell=True)
    current_step += 1

    # Adjust overlapping regions
    print_progress(current_step, total_steps, "Adjusting overlapping regions...")
    adjust_overlaps("sorted_output.bedGraph", "adjusted_output.bedGraph")
    current_step += 1

    # Convert bedGraph back to bigWig
    print_progress(current_step, total_steps, "Converting back to bigWig...")
    subprocess.run(["./bedGraphToBigWig", "adjusted_output.bedGraph", chrom_sizes_file, output_file])

    # Clean up intermediate files
    if clean_temp:
        for file in ["input.bedGraph", "output.bedGraph", "filtered_output.bedGraph", "clipped_output.bedGraph", "sorted_output.bedGraph", "adjusted_output.bedGraph"]:
            if os.path.exists(file):
                os.remove(file)

    print(f"\n\n🎉 Conversion complete! Output file: {output_file}")

# Example usage
# convert_bigwig("input_hg19.bw", "output_hg38.bw", "hg19", "hg38")
# convert_bigwig("input_hg38.bw", "output_hg19.bw", "hg38", "hg19", clean_temp=False)