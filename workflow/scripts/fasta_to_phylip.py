#!/usr/bin/env python3
__author__ = "tomarovsky"
from Bio import SeqIO
import argparse
import tarfile
import io

def extract(archive_path):
    fasta_content = ""
    
    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith(".fasta"):
                with tar.extractfile(member) as fasta_file:
                    fasta_content += fasta_file.read().decode("utf-8")
    return fasta_content

def main():
    fasta_content = extract(args.input)

    records = SeqIO.parse(io.StringIO(fasta_content), "fasta")
    SeqIO.write(records, args.output, "phylip")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="script for converting FASTA format to PHYLIP format")
    group_required = parser.add_argument_group("Required options")
    group_required.add_argument("-i", "--input", type=str, help="input concat FASTA file or stdin")
    group_required.add_argument("-t", "--type", type=str, help="molecular type (DNA, RNA or protein)")
    group_required.add_argument("-o", "--output", type=str, help="output NEXUS file name")
    args = parser.parse_args()
    main()
