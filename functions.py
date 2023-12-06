import os
import pandas as pd
from dash import dcc
import dash_bio as dashbio
import networkx as nx
import random
from scipy.stats import zscore
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
MAP_FILE =  'data/map_generated.csv'



def create_network(correlation_data,G):
    for index, row in correlation_data.iterrows():
        source_gene = row['SELECTED_GENE']
        target_gene = row['EVALUATED_GENE']
        correlation = row['CORRELATION']
        if not G.has_node(source_gene):
            G.add_node(source_gene, label=source_gene)
        if not G.has_node(target_gene):
            G.add_node(target_gene, label=target_gene)

        if not G.has_edge(source_gene, target_gene):
            G.add_edge(source_gene, target_gene, correlation=correlation)
        else:
            # If the edge already exists, update the correlation (or any other attributes)
            G[source_gene][target_gene]['correlation'] = correlation
       
    return G


def find_common_neighbors(G, gene_a, gene_b):
    neighbors_gene_a = list(G.neighbors(gene_a))
    neighbors_gene_b = list(G.neighbors(gene_b))
    common_neighbors = set(neighbors_gene_a).intersection(neighbors_gene_b)
    return list(common_neighbors)


def filter_network(input_value,THRESHOLD):

    map_df = pd.read_csv(MAP_FILE)
    nodes = []
    for gene in input_value:
        correlation_file = f"correlations/correlations_{gene}_by_chr.csv"
        correlation_data = pd.read_csv(correlation_file)
        data = pd.merge(correlation_data, map_df, left_on='EVALUATED_GENE', right_on='gene', how='left')[['SELECTED_GENE', 'EVALUATED_GENE', 'CORRELATION', 'PVALUE','chromosome', 'avg_pos']].drop_duplicates(subset='EVALUATED_GENE', keep='first')
        data = data[data['chromosome'] != 'chrX']
        data['nchromosome'] = data.chromosome.str[3:].astype(int)
       
        grouped = data.groupby('chromosome')
        filtered_data = pd.DataFrame()

        for _, group in grouped:
            # Calculate z-score for each 'nchromosome' group
   
            group['zscore'] = grouped['PVALUE'].transform(lambda x: zscore(np.log(x)))

            # Apply threshold filter for each 'nchromosome' group
            filtered_group = group[abs(group['zscore']).abs() > THRESHOLD]

            # Append the filtered results to the final DataFrame
            filtered_data = pd.concat([filtered_data, filtered_group])
        
        nodes.extend(filtered_data['EVALUATED_GENE'].unique())
 
    return list(set(nodes)),filtered_data






def get_data_in_dataframe(data):
    return ""

import plotly.graph_objs as go

def scatterplot_gene(input_value, THRESHOLD):
    # Load necessary data
    correlation_file = f"correlations/correlations_{input_value}_by_chr.csv"  
   
    map_df = pd.read_csv(MAP_FILE)
    if os.path.isfile(correlation_file):
        correlation_data = pd.read_csv(correlation_file)
        evaluated_gene_chromosome = map_df[map_df.gene == input_value].chromosome.tolist()[0] 
        print(map_df)
        # Merge dataframes and preprocess
        data = pd.merge(correlation_data, map_df, left_on='EVALUATED_GENE', right_on='gene', how='left')[
            ['SELECTED_GENE', 'EVALUATED_GENE', 'CORRELATION', 'PVALUE', 'chromosome', 'avg_pos']
        ].drop_duplicates(subset='EVALUATED_GENE', keep='first')
        data = data[data['chromosome'] != 'chrX']
        data['nchromosome'] = data.chromosome.str[3:].astype(int)
        data = data.sort_values(by=['nchromosome', 'avg_pos'])
        data['axis'] = data.nchromosome.astype(str) + '_' + data.avg_pos.astype(str)
        data['CORRELATION'] = round(data['CORRELATION'], 3)
        data['avg_pos'] = data['avg_pos'].astype(int)
        data = data[data.CORRELATION != 1]

        _, filtered_df = filter_network([input_value], THRESHOLD)
        filtered_df['axis'] = filtered_df.nchromosome.astype(str) + '_' + filtered_df.avg_pos.astype(str)
        # Create a figure and add traces for scatter plots
        
        data.reset_index(inplace = True)
        data = data.rename(columns={
        'SELECTED_GENE': 'SNP',
        'nchromosome': 'CHR',  # Column for the chromosome
        'avg_pos': 'BP',  # Column for the chromosomal position
        'PVALUE': 'P',  # Column for the quantity to be plotted on the y-axis
        'EVALUATED_GENE': 'GENE'  # Column for gene names
        })
        data['Filtered'] = data['GENE'].isin(filtered_df['EVALUATED_GENE'])
        data['Color'] = data['Filtered'].apply(lambda x: 'red' if x else 'blue')
        data.sort_values(by=['CHR','BP'])
       
        manhattanplot = px.scatter(
            data,
            x='CHR',  # Genomic positions along the chromosome
            y=-np.log(data['P']),  # -log10(p-value)
            color='Filtered',  # Color points by chromosome
            hover_data={'GENE': True,'CORRELATION': True},  # Display gene names on hover
            title='p-values obtained for the computed correlations for '+input_value+". Filtering " +str(THRESHOLD) + "SD above the mean per chromosome ",
            labels={'CHR': 'Chromosome', 'BP': 'Genomic Position (Base Pairs)', 'P': '-log10(p-value)'},
            color_discrete_sequence=['blue', 'red', 'green']  # Define color sequence for chromosomes
        )
        
        max_y = (-np.log(data['P'])).max() +20 # Get the max -log(p-value) for scaling
       
        manhattanplot.add_shape(
            type="rect",
            x0=int(evaluated_gene_chromosome[3:])-0.2,  # Start of the evaluated region
            x1=int(evaluated_gene_chromosome[3:])+0.2,  # End of the evaluated region
            y0=0,
            y1=max_y,
            fillcolor="rgba(211, 211, 211, 0.3)",  # Light gray with opacity
            line=dict(width=0),
        )

        # Update the axis labels
        manhattanplot.update_xaxes(title='Chromosome')
        manhattanplot.update_yaxes(title='-log10(p-value)')
        manhattanplot.update_traces(
            hovertemplate='<b>GENE</b>: %{customdata[0]}<br><b>CORRELATION</b>: %{customdata[1]}'
        )
        


        return manhattanplot
    
    return None



#  manhattanplot = dashbio.ManhattanPlot(
#             dataframe=DATASET,  
#             highlight = True, 
#             logp=True,  # Assuming you want to plot -log10(p-value)
#             title=f"Manhattan Plot for {input_value}",
#             ylabel='-log10(p)',
#             col = list(DATASET.Color.values)
#         )