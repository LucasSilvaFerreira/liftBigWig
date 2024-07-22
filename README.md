# liftBigWig
Lifting  bigwigs between human genome versions

# BigWig Converter

BigWig Converter is a Python package for converting bigWig files between hg19 and hg38 genome assemblies. It handles the conversion process, including coordinate mapping, chromosome filtering, and overlap adjustments.

## Features

- Convert bigWig files between hg19 and hg38 assemblies
- Filter out non-standard chromosomes
- Adjust overlapping regions
- Use UCSC tools for file format conversions
- Implement CrossMap for coordinate mapping
- Show progress with cool emoji-based messages

## Installation

```
pip install git+https://github.com/LucasSilvaFerreira/liftBigWig.git
```

## Usage

```python
from liftBigWig import convert_bigwig

# Convert from hg19 to hg38
convert_bigwig("input_hg19.bw", "output_hg38.bw", "hg19", "hg38")

# Convert from hg38 to hg19
convert_bigwig("input_hg38.bw", "output_hg19.bw", "hg38", "hg19")
```

## Function Parameters

- `input_file` (str): Path to the input bigWig file
- `output_file` (str): Path to save the output bigWig file
- `source_assembly` (str): Source assembly ('hg19' or 'hg38')
- `target_assembly` (str): Target assembly ('hg19' or 'hg38')
- `clean_temp` (bool, optional): Whether to remove temporary files after conversion. Defaults to True.

## Dependencies

- Python 3.6+
- CrossMap
- UCSC tools (automatically downloaded):
  - bigWigToBedGraph
  - bedGraphToBigWig
  - bedClip

## How It Works

1. Downloads necessary resources (UCSC tools and chain files)
2. Converts input bigWig to bedGraph
3. Uses CrossMap to convert coordinates between assemblies
4. Filters out non-standard chromosomes
5. Adjusts overlapping regions
6. Converts back to bigWig format

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

This tool uses UCSC Genome Browser utilities and CrossMap for coordinate conversion.
