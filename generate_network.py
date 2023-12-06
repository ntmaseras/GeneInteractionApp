import os
import pickle
import pandas as pd
import networkx as nx
from functions import create_network
import argparse
import time

LOG_FILE = 'app/network/network_summary_log.txt'  
NETWORK_FILE = 'app/network/gene_correlation.pickle'
PROCESSED_LOG = 'app/network/processed_genes.txt'
GENES_FILE = 'data/genes.txt'

def network(N):
    """
    Function to process genes and create a network based on correlations.

    Parameters:
    - N: Number of genes to process
    """

    # Load already processed genes from a log file
    processed_genes = []
    with open(PROCESSED_LOG, 'r') as file:
        processed_genes = file.read().splitlines()

    # Read the list of genes to process
    with open(GENES_FILE, 'r') as file:
        genes_list = [line.strip() for line in file.readlines()]

    # Load the existing network data or initialize a new one
    if os.path.exists(NETWORK_FILE):
        with open(NETWORK_FILE, 'rb') as file:
            G = pickle.load(file)
    else:
        G = nx.Graph()  

    n = 0
    for input_value in genes_list:
        print(input_value)
        correlation_file = f"correlations/correlations_{input_value}_by_chr.csv"

        # Process genes if not already processed and limit the count by N
        if input_value not in processed_genes and n < N:
            if os.path.exists(correlation_file):
                correlation_data = pd.read_csv(correlation_file)
                # Filter and plot correlations if required
                
                # Update the network with new correlation data
                G = create_network(correlation_data, G)
                # Update processed genes and log the entry
                processed_genes.append(input_value)
                with open(PROCESSED_LOG, 'a') as log:
                    log.write(input_value + '\n')
                
                 # Log summary statistics into the log file
                with open(LOG_FILE, 'a') as summary_log:
                    summary_log.write(f"Summary Statistics for Network at iteration {n}:\n")
                    summary_log.write(f"Number of nodes: {G.number_of_nodes()}\n")
                    summary_log.write(f"Number of edges: {G.number_of_edges()}\n")

            else:
                print("Gene not precomputed")
                print(input_value)
            n += 1
                        # Save the updated network data
        with open(NETWORK_FILE, 'wb') as file:
            pickle.dump(G, file)

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
    correlation_file = f"correlations/correlations_{input_gene}_by_chr.csv"

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
        network(N=6000)
        end_time = time.time()
        print(f"Time taken to generate the network: {end_time - start_time} seconds")
