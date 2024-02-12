import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import networkx as nx
import pandas as pd
import os
import pickle
import math
from dash import callback_context
# Your functions for network creation, filtering, and plotting
from functions import find_common_neighbors,filter_network,scatterplot_gene

import plotly.express as px
from PIL import Image

# Initialize the Dash app
app = dash.Dash(__name__)
NETWORK_FILE = 'network/gene_correlation.pickle'
if os.path.exists(NETWORK_FILE):
    with open(NETWORK_FILE, 'rb') as file:
        G = pickle.load(file)
else:
    G = None


node_positions = {}
elements = []
cytoscape = cyto.Cytoscape(
    id='network-graph',
    layout={'name': 'cose'},
    style={
        'width': '100%',
        'height': '600px',
        'edges': {'width': 2, 'color': 'black'},
        'node': {
            'backgroundColor': 'gray',  # Default node color
            'width': 3  # Default node width
        }
    },
    elements=[],
    boxSelectionEnabled=True,  # Enable box selection
    stylesheet=[
            # Group selectors
            {
            'selector': 'edge',
            'style': {
                'width': 'data(weight)',  # Mapping edge weight to width
                'line-color': '#ccc'  # Default edge color
            }
            },
             {
            'selector': 'edge:selected',
            'style': {
                'label': 'data(correlation)',
                'font-size': '6px',
                'color': 'black'
            }
            },
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'font-size': '5px',  # Adjust the font size of the node labels
                    'width': 10,  # Adjust the width of the nodes
                    'height': 10,  # Adjust the height of the nodes
                    'shape': 'ellipse'
                }
            },

            # Class selectors
            {
                'selector': '.red',
                'style': {
                    'background-color': 'red',
                    'line-color': 'red'
                }
            },
            {
                'selector': '.orange',
                'style': {
                    'background-color': 'orange',
                    'line-color': 'orange'
                }
            },
            {
                'selector': '.gray',
                'style': {
                    'background-color': 'gray',
                    'line-color': 'gray'
                }
            }
        ],
    responsive=True
)
nodes = []
# Prompt the user to select a gene
genes_file = 'data/genes.txt'
with open(genes_file, 'r') as file:
    genes_list = [line.strip() for line in file.readlines()]

# Scatter plot placeholders
scatterplot_1 = dcc.Graph(id='scatterplot-1')
scatterplot_2 = dcc.Graph(id='scatterplot-2')
app.layout = html.Div([
    html.H1("Gene Interaction Network"),
    html.Div([
        html.Div([
            html.Label("Select a gene:"),
            dcc.Dropdown(id='gene-dropdown-1',
                         options=[{'label': gene, 'value': gene} for gene in genes_list],
                         placeholder='Choose a gene'),
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Select a gene:"),
            dcc.Dropdown(id='gene-dropdown-2',
                         options=[{'label': gene, 'value': gene} for gene in genes_list],
                         placeholder='Choose a gene'),
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),
    ]),
    html.Div([
        html.Label('Select how many standard deviations (above the mean) you want to filter per chromosome:'),
        dcc.Slider(
            id='threshold-slider',
            min=0,  
            max=13,
            step=1,
            value=6,  # Initial threshold value
            marks={i: str(i) for i in range(13)},  # Marks on the slider
        ),
    ]),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='network-status'),
    html.Div([
        cytoscape,  # Display the Cytoscape graph here
    ], style={'width': '48%','height': '100%', 'display': 'inline-block'}),
    html.Div([
        scatterplot_1,  # Scatterplot for gene 1
        scatterplot_2,  # Scatterplot for gene 2
    ], style={'width': '48%','height':'30%', 'float': 'right', 'display': 'inline-block'}),
])

@app.callback(
    Output('network-status', 'children'),
    Output('network-graph', 'elements'),
    Output('scatterplot-1', 'figure'),
    Output('scatterplot-2', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('gene-dropdown-1', 'value'),
     State('gene-dropdown-2', 'value'),
     State('threshold-slider', 'value')]  # Added input for threshold value
)
def update_network_and_plots(n_clicks, gene_1, gene_2, threshold):
    elements = []
    scatterplot_1 = px.scatter()  # Default empty scatterplot
    scatterplot_2 = px.scatter()  # Default empty scatterplot

    if n_clicks > 0 and gene_1 and gene_2 and threshold:
        genes = [gene_1, gene_2]

        # Update network graph elements
        if G:
            if threshold is not None:
                selected_nodes,_ = filter_network([gene_1, gene_2], threshold)  # Apply filter using threshold value
                subgraph = nx.Graph(G.subgraph(set(selected_nodes) | {gene_1, gene_2}))
            else:
                subgraph = nx.Graph(G.subgraph(nx.ego_graph(G, genes[0]).nodes() | nx.ego_graph(G, genes[1]).nodes()))

            # Create network elements for Cytoscape
            subgraph.remove_nodes_from(list(nx.isolates(subgraph)))
            highlighted_nodes = set(subgraph.nodes())
            highlighted_edges = set(subgraph.edges())

            selected_nodes = set(genes)
            common_neighbors = set(find_common_neighbors(G, genes[0], genes[1]))
            rest_of_nodes = highlighted_nodes - selected_nodes - common_neighbors

            new_elements = [{'data': {'id': str(node), 'label': str(node)},
                             'classes': 'red' if node in selected_nodes else ('orange' if node in common_neighbors else 'gray')}
                            for node in highlighted_nodes]

            new_edges = []
            for edge in highlighted_edges:
                if edge[0] != edge[1]:
                    source, target = str(edge[0]), str(edge[1])
                    edge_data = subgraph.get_edge_data(edge[0], edge[1])
                    if edge_data is not None and 'correlation' in edge_data:
                        weight = edge_data['correlation']
                        new_edges.append({
                            'data': {
                                'source': source,
                                'target': target,
                                'weight': abs(weight),
                                'correlation': "Corr: " + str(round(weight, 2))
                            }
                        })

            elements = new_elements + new_edges

        # Update scatterplots
        scatterplot_1 = scatterplot_gene(gene_1, threshold)
        scatterplot_2 = scatterplot_gene(gene_2, threshold)

        # Return updated elements and scatterplots
        if elements:
            return html.Div("Network nodes and their neighbors are displayed. In red the selected genes and in yellow their common neighbors."), elements, scatterplot_1, scatterplot_2
        else:
            return html.Div("No network loaded or no neighbors found for the selected genes."), [], scatterplot_1, scatterplot_2

    return html.Div(""), [], scatterplot_1, scatterplot_2



if __name__ == '__main__':
    app.run_server(debug=True)