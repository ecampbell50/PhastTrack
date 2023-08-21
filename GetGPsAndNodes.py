######################################
######     Get GPs And Nodes    ######
######################################
# This script takes the column header#
# of the smash output and splits the #
# genome from prophage for the edges #
######################################

###### Dependencies ######

import pandas as pd
import argparse

########################### Define Functions  ####################################################

# Define function to load in matrix, split genome from prophage, and make an edgetable
def GPsAndPnodes(prophage_matrix):

    #################### Make Genome-Prophage Edgetable ####################

    # Load in the prophage matric csv from sourmash
    df_matrix = pd.read_csv(prophage_matrix)

    # Get the column header as a list
    unsplit_IDs_wfasta = list(df_matrix.columns)
    # Remove the string '.fasta' from all items
    unsplit_IDs = [item.rstrip('.fasta') for item in unsplit_IDs_wfasta]

    df_edges = pd.DataFrame({'Genome': unsplit_IDs})

    # Split the columns into genome and prophage
    df_edges[['GenomeID', 'ProphageID']] = df_edges['Genome'].str.split(pat='_', n=1, expand=True)

    # Drop the solo prophage column and switch the columns around Genome column
    df_edges.drop('ProphageID', axis=1, inplace=True)
    df_edges['Genome2'] = df_edges['Genome']
    df_edges.drop('Genome', axis=1, inplace=True)

    # Rename the columns to Genome1 and Genome2
    df_final = df_edges.rename(columns={'GenomeID': 'Genome1'})

    # Add a third column with values "GP"
    df_final['Value'] = 'GP'

    ######################
    # THIS IS THE GP EDGETABLE
    ######################
    df_final.to_csv("GenomesToProphages_Edgetable_GP.csv", index=False)

    #################### Make Prophage Node Table ####################

    # Extract Prophage column and value column set to Prophage as a dataframe
    df_Pmatrix = pd.read_csv("Prophage_Sourmash_JI.csv")
    Plist = list(df_Pmatrix.columns)
    Plist_nofasta = [item.rstrip('.fasta') for item in Plist]
    df_Plist = pd.DataFrame({'ID': Plist_nofasta})
    df_Plist['Type'] = 'Prophage'

    ######################
    # THIS IS THE PROPHAGE NODE TABLE
    ######################
    df_Plist.to_csv("ProphageNodeTable.csv", index=False)


# Define function to extract the column headers from the 
def Gnodes(genome_matrix):

    #################### Make Genome Node Table ####################

    # Load in the host genome sourmash output csv
    df = pd.read_csv(genome_matrix)

    # Make a list out of the header and remove the .fna
    ID_list_wfna = list(df.columns)
    ID_list = [item.rstrip('.fna') for item in ID_list_wfna]

    # Make a dataframe with the new IDs
    df_edges = pd.DataFrame({'ID': ID_list})

    # Add a new column for the genomes
    df_edges['Type'] = 'Genome'

    ######################
    # THIS IS THE GENOME NODE TABLE
    ######################
    df_edges.to_csv("GenomeNodeTable.csv", index=False)


################ Argparse ################
# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Arguments for editing the edge-table.')

# Add arguments to the parser
parser.add_argument('--prophage_input', type=str, help='Name of prophage sourmash output csv matrix file')
parser.add_argument('--genome_input', type=str, help='Name of genome sourmash output csv matrix file')

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the arguments
genome_input_csv = args.genome_input
prophage_input_csv = args.prophage_input

###########################################

################ Use Functions ################
GPsAndPnodes(prophage_input_csv)
Gnodes(genome_input_csv)
###############################################

# Now to concatenate the edge tables together and the node tables together

# First read in all edgetables
df_GG = pd.read_csv("Host_Sourmash_JI_Edgetable_GG.csv")
df_PP = pd.read_csv("Prophage_Sourmash_JI_Edgetable_PP.csv")
df_GP = pd.read_csv("GenomesToProphages_Edgetable_GP.csv")

# Remove .fna from the GG table
df_GG_edited = df_GG.applymap(lambda x: x.replace('.fna', ''))
# Remove .fasta from the PP table
df_PP_edited = df_PP.applymap(lambda x: x.replace('.fasta', ''))

# Concatenate all 3 edgetables
concatenated_df = pd.concat([df_GG_edited, df_PP_edited, df_GP], axis=0)
# Reset the index just in-caseys
concatenated_df.reset_index(drop=True, inplace=True)

# Save the concatenated df
concatenated_df.to_csv("Final_GG-PP-GP_Edgetable.csv", index=False)

# Now to concatenate the node tables together

# Read in the two node tables
df_Gnodes = pd.read_csv("GenomeNodeTable.csv")
df_Pnodes = pd.read_csv("ProphageNodeTable.csv")

# Join them together
concatNodes_df = pd.concat([df_Gnodes, df_Pnodes], axis=0)
concatNodes_df.reset_index(drop=True, inplace=True)

# Save it as a csv
concatNodes_df.to_csv("NodeTable_Final.csv", index=False)
