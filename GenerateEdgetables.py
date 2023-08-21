######################################
######  Convert S.mash Output   ######
######################################
# This script takes the output of s- #
# ourmash and converts it to an edge #
# table to be used in cytoscape etc. #
######################################

###### Dependencies ######

import pandas as pd
import argparse

########################### Define Functions  ####################################################

# Make an edge table from the original matrix.csv from sourmash
def smashpass_edgetable(smash_csv, SIM, con_type):
        # smash_csv = the sourmash output csv to be converted to an edgetable
        # SIM = the minimum similarity for a connection (0.6 == 60% similarity)
        # TYPE = the type of connection: Genome-Genome (GG), Genome-Prophage (GP), Prophage-Prophage (PP)

        # Define output csv
        # Find the position of the file extension ".csv"
        extension_index = smash_csv.rfind(".csv")
        # Extract the part of the string before the file extension
        filename_without_extension = smash_csv[:extension_index]
        # Create a the new filename by concatenating "_Edgetable.csv" to the extracted part
        OUTPUT = filename_without_extension + "_Edgetable_" + con_type + ".csv"

        # Read in the csv matrix input
        csv = pd.read_csv(smash_csv)
        # Convert column headers to integers (for counting across as many down)
        csv.columns = range(len(csv.columns))
        # Create an empty list to store the converted data
        new_data = []

        # Iterate through each column, taking each value until the index=column header
        # As when index=column header, it'll be the 1 diagonal from the matrix
        for col_idx in csv.columns:
                for idx, val in csv[col_idx].items():
                # Only add the value if the index is less than or equal to the column header
                        if idx <= col_idx:
                                new_data.append({"Genome1": col_idx, "Genome2": idx, "Value": val})

        # Create a new dataframe from the new_data list
        df = pd.DataFrame(new_data)
        df_for_step2 = df.copy()

        # Change the integer headers back to genome IDs
        # Make a dictionary for GenomeIDs->integers
        dict_csv = pd.read_csv(smash_csv)
        genome_IDs = list(dict_csv.columns)
        genome_IDs_dict = {idx: val for idx, val in enumerate(genome_IDs)}
        # Replace the integers with genome IDs
        df_for_step2["Genome1"] = df_for_step2["Genome1"].map(genome_IDs_dict)
        df_for_step2["Genome2"] = df_for_step2["Genome2"].map(genome_IDs_dict)

        # Remove any edges that are less than the defined similarity
        filtered_df = df_for_step2[df_for_step2.iloc[:, 2] >= SIM]

        # Remove any rows where the first and second column are the same (self loop)
        final_df = filtered_df[filtered_df['Genome1'] != filtered_df['Genome2']]

        # Change all similarity values to the connection type
        final_df.loc[:, 'Value'] = con_type


        # Convert the df to a csv
        final_df.to_csv(OUTPUT, index=False, header=True)



###################################################################################################

################ Argparse ################
# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Arguments for editing the edge-table.')

# Add arguments to the parser
parser.add_argument('--input', help='Name of sourmash output csv file')
parser.add_argument('--sim', type=float, help='Float value of edges to remove, less than the given value')
parser.add_argument('--type', type=str, help='Type of connection between nodes. Genome-Genome = GG, Prophage-Prophage = PP')

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the arguments
input_file = args.input
sim_val = args.sim
con_type = args.type

################ Use Functions ################
smashpass_edgetable(input_file, sim_val, con_type)
