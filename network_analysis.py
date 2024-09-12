# Loading libraries
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

# Loading df
df = read.csv("nopd_misconduct.csv")

# Creating a list of unique tracking id's
uid_summary = (df
                .groupby('tracking_id')['uid']
                .unique()
                .reset_index(name='uid_list'))

# Creating a vector of id's
uid_vector = pd.unique(np.concatenate(uid_summary['uid_list'].values))

# Creating a id matrix
uid_matrix = pd.DataFrame(0, index=uid_vector, columns=uid_vector)

# Populating the matrix with co-accusals
for uids in uid_summary['uid_list']:
    if len(uids) > 1:
        for i in range(len(uids)):
            for j in range(i + 1, len(uids)):
                uid_matrix.at[uids[i], uids[j]] = 1
                uid_matrix.at[uids[j], uids[i]] = 1

# Turning this adjacency matrix into a graph
G = nx.from_pandas_adjacency(uid_matrix)

# Defining attributes
node_attributes = (filtered_df[['uid', 'race', 'sex']]
                    .drop_duplicates()
                    .set_index('uid'))

# Adding attributes to the nodes
nx.set_node_attributes(G, node_attributes['race'].to_dict(), 'race')
nx.set_node_attributes(G, node_attributes['sex'].to_dict(), 'sex')

# Adding colors for each race and gender
race_colors = {"white": "lightblue", "black": "lightgreen", "hispanic": "lightcoral", "asian / pacific islander": "lightyellow", "native american": "lightgray"}
gender_colors = {"male": "blue", "female": "pink"}

# Defining degree thresholds
bottom_degree_threshold = 20
top_degree_threshold = 40

# Filtering nodes based on thresholds
filtered_nodes = [node for node, degree in dict(G.degree()).items() if bottom_degree_threshold <= degree <= top_degree_threshold]

# Creating a subgraph
G_sub = G.subgraph(filtered_nodes)

# Creating the plot
plt.figure(figsize=(14, 12))
pos = nx.spring_layout(G_sub, k=1, iterations=5) 

# Plotting the graph with racial demographics
plt.figure(figsize=(14, 12))
nx.draw(G_sub, pos, with_labels=False, node_size=100, edge_color='lightgray', alpha=0.5, 
        node_color=[race_colors.get(G_sub.nodes[n].get('race', 'other').lower(), 'gray') for n in G_sub.nodes], width=0.1)
plt.title("Subgraph Colored by Race")
plt.show()

# Plotting the graph with gender demographics
plt.figure(figsize=(12, 10))
nx.draw(G_sub, pos, with_labels=False, node_size=50, edge_color='lightgray', alpha=0.5, 
        node_color=[gender_colors.get(G_sub.nodes[n].get('sex', 'unknown').lower(), 'gray') for n in G_sub.nodes],width=0.1)
plt.title("Subgraph Colored by Gender")
plt.show()

# Creating a component dataframe
connected_components = list(nx.connected_components(G))

subgraph_info = []

for idx, component in enumerate(connected_components):
    component_nodes = list(component)
    subgraph_info.append({
        'subgraph_id': idx,
        'uid_list': component_nodes,
        'num_uids': len(component_nodes)
    })

subgraph_df = pd.DataFrame(subgraph_info)

print(subgraph_df)
