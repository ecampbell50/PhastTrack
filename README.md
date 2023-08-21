# PhastTrack
Pipeline to go straight from genome fasta files to prophage network analysis

What it does:
Uses geNomad to find proviruses (prophages if bacteria) within fasta (.fna) files, extracts individual prophage sequences, and runs sourmash to compare each genome to each other and each prophage to each other. An edgetable is then created where only edges of similarity 60% or more are kept (can be changed on line 158 and 159 on NetworkAnalysis.sh, change ```--sim 0.6``` to the min similarity to keep from 0-1). Final output is an edgetable and node table to be uploaded into cytoscape. General sourmash and geNomad outputs are there too if needed.


#### Dependencies for this pipeline to work ####
- Mamba
- Genomad (installed with mamba): https://portal.nersc.gov/genomad/installation.html

   **NB: install genomad into an environment called "genomad2" otherwise will not run. Otherwise go to line 40 of NetworkAnalysis.sh and change ```mamba run -n genomad2``` to whatever your env is called **
- Genomad database: doesn't take that long to download ```genomad download-database .```
- Numpy v1.24 (genomad may not install the right version)
``` pip install --user numpy==1.24 ```
- Sourmash
``` pip install --user sourmash ```
- pandas and argparse installed in your environment

Getting Started
- Make sure NetworkAnalysis.sh, GetGPsAndNodes.py, GenerateEdgetables.py, genomad_db and all fasta files (WITH SUFFIX '.fna') are in the same directory
- Fasta files CANNOT have underscores (_) in the name, the python script which splits the genome name from the prophage ID uses underscores as a delimiter
- The sbatch script PhastTrack.sh is a suggestion, but genomad is set to run with the ```--threads 32``` parameter. If you want to change the amount of threads to use, go to line 40 of NetworkAnalysis.sh
- Similarly, go to the same line if you want to edit any other genomad parameters. I'm using the ```--conservative``` and ```--conservative-taxonomy``` parameters for my work, but change if needed
- if you want to change the memory/cpu requirements, as a guide: 10 Streptococcus suis (~2Mb) genomes took roughly 20 minutes with 128G mem and 32 cpus

Results
- Sourmash results will be in the Sourmash directory
- Final edgetable and node table for use in cytoscape will be in the Edgetable directory. Saved as Final_GG-PP-GP_Edgetable.csv and NodeTable_Final.csv. Should be able to colour prophages and genomes differently to find clusters
- Genomad outputs will stay saved in the generated directory (based on date ran)
