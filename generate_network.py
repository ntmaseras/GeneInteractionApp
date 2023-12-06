import os
import pickle
import pandas as pd
import networkx as nx
from functions import create_network 
import argparse
import time

LOG_FILE = 'network/network_summary_log.txt'  
NETWORK_FILE = 'network/gene_correlation.pickle'
PROCESSED_LOG = 'network/processed_genes.txt'
GENES_FILE = 'data/genes.txt'
def network():
    
    processed_genes = []
    with open(PROCESSED_LOG, 'r') as file:  
        processed_genes = file.read().splitlines()

    genes_file = 'data/genes.txt'
    with open(genes_file, 'r') as file:
        genes_list = [line.strip() for line in file.readlines()]
    with open(NETWORK_FILE, 'rb') as file:
        G = nx.Graph()
    i=0
    for input_value in genes_list:
        correlation_file = f"correlations/correlations_{input_value}_by_chr.csv"
        #print(correlation_file)
        if input_value not in processed_genes:
            if os.path.exists(correlation_file):
                correlation_data = pd.read_csv(correlation_file)
                G = create_network(correlation_data, G)
                processed_genes.append(input_value)
                with open(PROCESSED_LOG, 'a') as log:
                    log.write(input_value + '\n')
                with open(NETWORK_FILE, 'wb') as file:
                    pickle.dump(G, file)

            else:
                print(correlation_file)
                print("Gene not precomputed")
            print(i)
            i+=1
        
    print("Number of nodes:")
    print(len(list(G.nodes())))
        

def add_gene(input_gene):
    """
    Function to add information about a selected gene to the network.

    Parameters:
    - input_gene: Gene for which information needs to be added
    """

    # Load the existing network data
    if os.path.exists(NETWORK_FILE):
        with open(NETWORK_FILE, 'rb') as file:
            G = pickle.load(file)
    else:
        G = nx.Graph()  # Create a new network if none exists

    # Create the file path for the gene data
    correlation_file = f"output/correlations/correlations_{input_gene}_by_chr.csv"

    # Process the gene if the corresponding file exists
    if os.path.exists(correlation_file):
        correlation_data = pd.read_csv(correlation_file)
        # Update the network with new correlation data for the given gene
        G = create_network(correlation_data, G)
        print("Number of nodes in the updated network:")
        print(len(list(G.nodes())))

        # Save the updated network data back to the pickle file
        with open(NETWORK_FILE, 'wb') as file:
            pickle.dump(G, file)
    else:
        print("Gene data not found for", input_gene)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process genes and create a network or add information about a gene.')
    parser.add_argument('--gene', type=str, help='Add information about a specific gene to the network')

    args = parser.parse_args()

    if args.gene:
        start_time = time.time()
        add_gene(args.gene)
        end_time = time.time()
        print(f"Time taken to add information about {args.gene}: {end_time - start_time} seconds")
    else:
        start_time = time.time()
        network()
        end_time = time.time()
        print(f"Time taken to generate the network: {end_time - start_time} seconds")

