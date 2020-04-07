import argparse
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def main():
    parser = argparse.ArgumentParser(description="Plotting 10x clusters.")
    parser.add_argument("--scmatch", metavar="CSV", required=True,
                        help="scMatch celltype CSV")
    parser.add_argument("--tsne", metavar="CSV", required=True,
                        help="Cellranger tSNE output")
    parser.add_argument("--clusters", metavar="CSV(s)",
                        nargs="+", required=True,
                        help="Cellranger clusters")
    args = parser.parse_args()
    colors = [
        "#ff0000", "#ffaa00", "#90d900", "#00f2e2", "#0088ff", "#7a00e6", 
        "#a60042", "#730f00", "#996600", "#558000", "#00736b", "#0058a6", 
        "#5e008c", "#ff0044", "#bf3300", "#332200", "#1fe600", "#00b3bf", 
        "#002240", "#ca00d9", "#66001b", "#401100", "#bf9900", "#00a642", 
        "#003c40", "#0061f2", "#530059", "#a60016", "#f26100", "#665200", 
        "#005924", "#00ccff", "#002966", "#300033", "#330007", "#7f3300", 
        "#eeff00", "#00331b", "#005c73", "#002ca6", "#e60099", "#cc6d00", 
        "#9ba600", "#00ffaa", "#00aaff", "#000e66", "#800055", "#593000", 
        "#334000", "#00a685", "#006699", "#000733", "#590030"
    ]
    celltype_df = pd.read_csv(args.scmatch)
    tsne_df = pd.read_csv(args.tsne)
    plot_celltype_to_tsne(celltype_df, tsne_df, "1_celltype_to_tsne.png",
                          colors)
    clust_df = pd.read_csv(args.clusters[0])
    plot_celltype_against_clusters(celltype_df, tsne_df, clust_df,
                                   "knn Clusters",
                                   "2_celltype_to_knn_lmo_cluster.png",
                                   colors)
    for i, clust in enumerate(args.clusters[1:]):
        clust_df = pd.read_csv(clust)
        filename = "%i_celltype_to_kmeans_%i_cluster.png" % (i+3, i+2)
        plot_title = "%i Cluster Kmeans" % (i+1)
        plot_celltype_against_clusters(celltype_df,
                                       tsne_df,
                                       clust_df,
                                       plot_title,
                                       filename,
                                       colors)


def plot_celltype_to_tsne(celltype_df, tsne_df, filename, colors):
    '''Plots the cell types from scMatch onto tSNE projection.'''
    plt.rcParams['figure.figsize'] = [15, 15]
    combined_df = tsne_df.join(celltype_df, lsuffix='cell', rsuffix='Barcode')
    if len(combined_df['cell type'].unique()) > len(colors):
        repeat_scal = math.ceil(
            len(combined_df['cell type'].unique()) / len(colors)
        )
        full_colors = colors * repeat_scal
    else:
        full_colors = colors
    for i, celltype in enumerate(combined_df['cell type'].unique()):
        x = combined_df.loc[combined_df['cell type'] == celltype, 'TSNE-1']
        y = combined_df.loc[combined_df['cell type'] == celltype, 'TSNE-2']
        a = combined_df.loc[
            combined_df['cell type'] == celltype, 
            'top correlation score'
        ]
        for vals in zip(x, y, a):
            x1, y1, a1, = vals
            try:
                plt.scatter(x1, y1, c=full_colors[i], alpha=a1, label=celltype)
            except IndexError as e:
                print(e)
                print(i, len(colors))
                import sys
                sys.exit()
    plt.title("scMatch Cell Type Overlay onto tSNE")
    legend_elements = [Line2D([0], [0],
                              marker='o',
                              color='w',
                              label=v,
                              markerfacecolor=c,
                              markersize=10)
                       for c, v in zip(colors, 
                                       combined_df['cell type'].unique())]
    plt.legend(handles=legend_elements,
               loc='center left',
               bbox_to_anchor=(1, 0.5))
    plt.savefig(filename, bbox_inches="tight")
    
    
def plot_celltype_against_clusters(celltype_df, tsne_df, clust_df, 
                                   cluster_title, filename, colors):
    '''Plots 2x1 plots of cell types against the produced clusters.'''
    combined_df = tsne_df.join(celltype_df, lsuffix='cell', rsuffix='Barcode')
    combined_df = combined_df.join(clust_df, 
                                   lsuffix='Barcode',
                                   rsuffix='Barcode')
    if len(combined_df['cell type'].unique()) > len(colors):
        repeat_scal = math.ceil(
            len(combined_df['cell type'].unique()) / len(colors)
        )
        full_colors = colors * repeat_scal
    else:
        full_colors = colors
    fig, axs = plt.subplots(1,2, figsize=(35, 15), sharey=True, sharex=True)
    for i, celltype in enumerate(combined_df['cell type'].unique()):
        x = combined_df.loc[combined_df['cell type'] == celltype, 'TSNE-1']
        y = combined_df.loc[combined_df['cell type'] == celltype, 'TSNE-2']
        a = combined_df.loc[combined_df['cell type'] == celltype, 'top correlation score']
        for vals in zip(x, y, a):
            x1, y1, a1, = vals
            axs[0].scatter(x1, y1, c=full_colors[i], alpha=a1, label=celltype)
    legend_elements = [Line2D([0], [0],
                              marker='o',
                              color='w',
                              label=v,
                              markerfacecolor=c,
                              markersize=10)
                       for c, v in zip(full_colors, combined_df['cell type'].unique())]
    axs[0].legend(handles=legend_elements,
                  loc='center left',
                  bbox_to_anchor=(1, 0.5))
    axs[0].set_title("celltype")
    for i, clust in enumerate(sorted(combined_df['Cluster'].unique())):
        x = combined_df.loc[combined_df['Cluster'] == clust, 'TSNE-1']
        y = combined_df.loc[combined_df['Cluster'] == clust, 'TSNE-2']
        axs[1].scatter(x, y, c=full_colors[i], label=clust)
    axs[1].set_title(cluster_title)
    axs[1].legend(loc="center left", bbox_to_anchor=(1, 0.5))
    fig.tight_layout()
    plt.savefig(filename)


if __name__ == "__main__":
    main()
