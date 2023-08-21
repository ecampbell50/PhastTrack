#!/bin/bash
#############################
# Network Analysis Pipeline #
#############################
# This pipeline takes genome fasta files, identifies prophages and -     #
# runs sourmash to check for similarities between genomes and prophages. #
# It then reformats the data to be used in cytoscape.                    #

###Variables###
time=$(date +"%H:%M:%S")
date=$(date +"%Y-%m-%d")
log_file="NetworkPipeline_${date}.log"
run_id="NP_${date}_${time}"
output_dir="NetAnalysis_$date"
working_dir="$PWD"

### Make Output Directory ###
mkdir -p $output_dir
mkdir -p $output_dir/logs
##################Log##################
echo "Current working directory: $working_dir" >> $output_dir/logs/"$log_file"
echo "$date + $time" >> $output_dir/logs/"$log_file"
echo 'Genome/Prophage network pipeline' $output_dir/logs/"$log_file"
echo "Run ID: ${run_id}" >> $output_dir/logs/"$log_file"
######################################

######## Script Start ########

############################################ geNomad ############################################
echo $(date +"%H:%M:%S") + " - Starting geNomad to identify prophages from input sequences" >> $output_dir/logs/"$log_file"

# First thing is to run geNomad on fasta files
# Learn how to specify input directories and things later

# Loop through the fasta files in the current directory
fastafiles=`ls *.fna | wc -l`
echo $(date +"%H:%M:%S") + " - Number of genomes: $fastafiles" >> $output_dir/logs/"$log_file"
for i in *.fna;
do
    mamba run -n genomad2 genomad end-to-end --conservative --threads 32 --conservative-taxonomy $i $output_dir/${i//.fna}_GenomadOutput genomad_db
    echo $(date +"%H:%M:%S") + " - Genome $i completed..." >> $output_dir/logs/"$log_file"
done
echo '~ geNomad has finished ~' >> $output_dir/logs/"$log_file"
genomad_output_dirs=`ls -d $output_dir/*_GenomadOutput | wc -l`
echo $(date +"%H:%M:%S") + " - Number of geNomad output directories: $genomad_output_dirs"

# Extract fnas and tsvs from genomad outputs
mkdir -p $working_dir/$output_dir/Provirus_tsvs
mkdir -p $working_dir/$output_dir/Provirus_fnas

# Move the genomad provirus tsvs and fnas to the new dir
cd $working_dir/$output_dir/

for i in *_GenomadOutput;
do
    mv $i/${i//_GenomadOutput}_find_proviruses/${i//_GenomadOutput}_provirus.fna $working_dir/$output_dir/Provirus_fnas/
    mv $i/${i//_GenomadOutput}_find_proviruses/${i//_GenomadOutput}_provirus.tsv $working_dir/$output_dir/Provirus_tsvs/
done
echo $(date +"%H:%M:%S") + " - fnas and tsvs moved to new directories" >> $working_dir/$output_dir/logs/"$log_file"


#### Extract Prophage Sequences ####

echo $(date +"%H:%M:%S") + " - extracting prophage sequences and creating new fasta files..." >> $working_dir/$output_dir/logs/"$log_file"

num_prophages=`ls $working_dir/$output_dir/Provirus_fnas/*.fna | wc -l` 
echo $(date +"%H:%M:%S") + " - Total number of files to convert: $num_prophages" >> $working_dir/$output_dir/logs/"$log_file"

cd $working_dir/$output_dir/Provirus_fnas
mkdir -p split_fastas

# Edit the pipe (|) in each fna file so that it's not bothersome in file names
for i in *.fna;
do
    sed -i 's/|/-/g' $i
    sed -i 's/.con./-/g' $i
done

# Extract contigs (individual prophages) from genomad outputs
for file in *provirus.fna;
do
	while IFS= read -r line
	do
		if [[ ${line:0:1} == '>' ]]
		then
			outfile="split_fastas/${file//_provirus.fna}_${line#>}.fasta"
			echo "$line" > "$outfile"
		else
			echo "$line" >> "$outfile"
		fi
	done < "$file"
done

num_fasta=`ls $working_dir/$output_dir/Provirus_fnas/split_fastas/*fasta | wc -l`
echo $(date +"%H:%M:%S") + " - Total number of files converted: $num_fasta" >> $working_dir/$output_dir/logs/"$log_file"


############################################ Sourmash ############################################
# Organise directories for Sourmash
cd $working_dir/$output_dir
mkdir -p Sourmash
mkdir -p Sourmash/Genome_signatures
mkdir -p Sourmash/Provirus_signatures

#### Sourmash Compute ####
# Run sourmash on genomes, and move the signature files to the new directory
cd $working_dir
smash_check_genomes=`ls *.fna | wc -l`
echo $(date +"%H:%M:%S") + " - Total number of genome fastas for sourmash: $smash_check_genomes" >> $working_dir/$output_dir/logs/"$log_file"

sourmash sketch dna -p k=31,scaled=1000 *.fna

smash_check_genomes_sigs=`ls *.sig | wc -l`
echo $(date +"%H:%M:%S") + " - Total number of genome signatures: $smash_check_genomes_sigs" >> $working_dir/$output_dir/logs/"$log_file"

mv *.sig $working_dir/$output_dir/Sourmash/Genome_signatures/

# Run sourmash on prophages, and move the signature files to the new directory
cd $working_dir/$output_dir/Provirus_fnas/split_fastas
smash_check_prophages=`ls *.fasta | wc -l`
echo $(date +"%H:%M:%S") + " - Total number of prophage fastas for sourmash: $smash_check_prophages" >> $working_dir/$output_dir/logs/"$log_file"

sourmash sketch dna -p k=21,scaled=1000 *.fasta

smash_check_prophages_sigs=`ls *.sig | wc -l`
echo $(date +"%H:%M:%S") + " - Total number of prophage signatures: $smash_check_prophage_sigs" >> $working_dir/$output_dir/logs/"$log_file"

mv *.sig $working_dir/$output_dir/Sourmash/Provirus_signatures/

#### Sourmash Compare ####
# Run sourmash compare on the genome signatures
cd $working_dir/$output_dir/Sourmash/Genome_signatures
sourmash compare --ksize 31 --output Host_Sourmash_JI.binary --csv Host_Sourmash_JI.csv *.sig
echo $(date +"%H:%M:%S") + " - Host sourmash complete" >> $working_dir/$output_dir/logs/"$log_file"

# Run sourmash compare on the prophage signatures
cd $working_dir/$output_dir/Sourmash/Provirus_signatures
sourmash compare --ksize 21 --output Prophage_Sourmash_JI.binary --csv Prophage_Sourmash_JI.csv *.sig
echo $(date +"%H:%M:%S") + " - Prophage sourmash complete" >> $working_dir/$output_dir/logs/"$log_file"

#### Sourmash Plot ####
# Get graphs for both runs
cd $working_dir/$output_dir/Sourmash/Genome_signatures
sourmash plot --output-dir $working_dir/$output_dir/Sourmash *.binary

cd $working_dir/$output_dir/Sourmash/Provirus_signatures
sourmash plot --output-dir $working_dir/$output_dir/Sourmash *.binary


############################################ Making Edgetables ############################################
cd $working_dir/$output_dir
mkdir -p Edgetables
cd $working_dir/$output_dir/Edgetables

mv $working_dir/$output_dir/Sourmash/Genome_signatures/*.csv $working_dir/$output_dir/Edgetables/
mv $working_dir/$output_dir/Sourmash/Provirus_signatures/*.csv $working_dir/$output_dir/Edgetables/

python3 $working_dir/GenerateEdgetables.py --input Host_Sourmash_JI.csv --sim 0.6 --type GG
python3 $working_dir/GenerateEdgetables.py --input Prophage_Sourmash_JI.csv --sim 0.6 --type PP


############################################ Getting Edgetable for G-P Connections ############################################
# Move to the directory
cd $working_dir/$output_dir/Edgetables

python3 $working_dir/GetGPsAndNodes.py --input_prophage Prophage_Sourmash_JI.csv --input_genome Host_Sourmash_JI.csv

echo "Final Edge and Node tables saved to $working/$output_dir/Edgetables"

##### END OF SCRIPT #####
# cd back to the working directory
cd $working_dir
