Report for 10x single cell type matching and differential expression analysis
---

This document discusses the steps that were performed in the analysis pipeline.  It also describes the format of the output files and some brief interpretation.  For more detailed questions about interpretation of results, consult the documentation of the various tools.


## Outputs:

This section describes the contents of the delivered results.

#### Cellranger gene expression counting

- Sparse matrices for gene expression for each barcode are provided as:
    - Raw and filtered counts
    - CSV (comma delimited files) and HDF5 file formats
- Differential Expression analysis
    - XLSX (Excel) files of differential gene expressions based on the unsupervised clusters (against background)
        - Cellranger's graph based clustering method
        - K-means clustering for 2 - 10 clusters
- Cell type matching
    - CSV (comma delimited file) of top match for each barcode
        - cell type
        - correlation score for that cell type
    - XLSX file(s) for top 3 matches for each barcode
        - cell type
        - correlation score for that cell type
- Report
    - cell type matching projected onto the tSNE plot
    - cell type matched tSNE plot compared to overlays of:
        - the graph based clustering
        - 2 - 10 cluster KMeans clustering

#### Main results

The main results are contained in one zip archive. This should be downloaded locally and "unzipped" on your local computer. It contains several sub-directories which contain files produced in each step of the pipeline.

- **QC**
    - This directory contains an HTML-based QC report which summarizes the read quality, alignment quality, and other metrics. It was produced by Cellranger.
- **Differential Expression**
    - XLSX (Excel) files of differential gene expressions based on the unsupervised clusters (against background)
        - Cellranger's graph based clustering method
        - K-means clustering for 2 - 10 clusters
- **Report**
    - This report will display the images for:
        - Cell type matching to tSNE projection
        - Comparison of cell type matching to unsupervised clustering:
            - Cellranger's graph based clustering method
            - K-means clustering for 2 - 10 clusters


## Methods:

Input FASTQ-format files are aligned, demultiplexed by molecular barcode, gene expression counted, and clustering with Cellranger {{cellranger_version}} [1]. The FASTQ reads are then aligned to the {{genome}} reference genome using the STAR aligner[2]. The aligned reads are then UMI counted and assigned with filtering for sequencing-based substitution errors.

Dimensionality reduction with Principal Component Analysis (PCA) is performed up to 10 components. These 10 PCA components are then used in t-disctributed stochastic neighbor embedding (t-SNE) to better visualize the clustering of cells by their gene expression (to 2 components). Unsupervised clustering is done by two methods: k-means clustering [] and Cellranger's implementation of a graph based clustering method. The graph based clustering method "consists of building a sparse nearest-neighbor graph (where cells are linked if they among the k nearest Euclidean neighbors of one another), followed by Louvain Modularity Optimization (LMO; Blondel, Guillaume, Lambiotte, & Lefebvre, 2008), an algorithm which seeks to find highly-connected "modules" in the graph. The value of k, the number of nearest neighbors, is set to scale logarithmically with the number of cells. An additional cluster-merging step is done: Perform hierarchical clustering on the cluster-medoids in PCA space and merge pairs of sibling clusters if there are no genes differentially expressed between them (with Benjamini-Hochberg adjusted p-value below 0.05). The hierarchical clustering and merging is repeated until there are no more cluster-pairs to merge." [] The 10 PCA components act as the input for both clustering methods. K-means clustering requires a prior assumption of the number of clusters, so two through ten clusters are used as the cluster number.

Differential expression is performed with Cellranger's implementation of sSeq []. It involves a two step process of obtaining the estimates for each genes using the method of moments, then regularizing the estimates. The specific contrast groups for the exact differential expression is pairwise comparisons of each cluster (both the graph based and k-means clustering approaches) to the backgroud - i.e. all clusters combined.

Cell type matching is done with scMatch. [] scMatch annotates single cells by identifying it's closest match from large reference datasets - FANTOM5. The match is calculated by Spearman ranked correlation. The version used for scMatch can be found at {{scmatch_url}} with a git commit hash of {{scmatch_hash}}.


## Inputs:

Sequencing FASTQ files in a gzipped tarbell (.tar.gz).

## Version control:
To facilitate reproducible analyses, the analysis pipeline used to process the data is kept under git-based version control.  The repository for this workflow is at 

<{{git_repo}}>

and the commit version was {{git_commit}}.

This allows us to run the *exact* same pipeline at any later time, discarding any updates or changes in the process that may have been added.

## Plots

### Cell type matching

### Comparison of cell type matches to unsupervised Clusters
![]( {{celltype_clust}} )
##### Graph based clustering
![]( {{graph_clust}} )
##### K-means clustering

{% for obj in kmeans_clust %}

![]( {{obj}} )

{% endfor %}


#### References:

[1] 

van der Maaten, L.J.P.; Hinton, G.E. (Nov 2008). "Visualizing Data Using t-SNE" (PDF). Journal of Machine Learning Research. 9: 2579–2605.

Lloyd, Stuart P. (1957). "Least square quantization in PCM". Bell Telephone Laboratories Paper. Published in journal much later: Lloyd, Stuart P. (1982). "Least squares quantization in PCM" (PDF). IEEE Transactions on Information Theory. 28 (2): 129–137. CiteSeerX 10.1.1.131.1338. doi:10.1109/TIT.1982.1056489. Retrieved 2009-04-15.

https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/algorithms/overview

Yu D, Huber W, Vitek O (2019). sSeq: Shrinkage estimation of dispersion in Negative Binomial models for RNA-seq experiments with small sample size. R package version 1.22.0. 