workflow ReportSingleCell10xMockWorkflow {

}

task create_plots {
    clusts=$(find . -name "*.csv" | sort -V)
}

task generate_report {
    File zipped_cellranger_output

    # runtime commands
    Int disk_size = 200

    command {
        mkdir data;
        tar xzf ${zipped_cellranger_output} -C data --strip-components 1;
        clusts=$(find ./data/outs/analysis/clustering/ -name "*.csv" | sort -V)
        python /opt/software/plotting.py \
            --scmatch ./data/outs/filtered_feature_bc_matrix/annotation_result_keep_expressed_genes/human_Spearman_top_ann.csv \
            --tsne ./data/outs/analysis/tsne/2_components/projection.csv \
            --clusters ${clusts};
        kmeansclusts=$(ls *kmeans*_cluster.png);
        python /opt/software/generate_report.py \
            --celltype 1_celltype_to_tsne.png \
            --graphcluster 2_celltype_to_knn_lmo_cluster.png \
            --kmeans ${kmeansclusts} \
            -j config.json \
            -t /opt/report/report.md \
            -o completed_report.md;
        pandoc \
            -H /opt/report/report.css \
            -s completed_report.md \
            -o analysis_report.html;
    }

    output {
        File report = "analysis_report.html"
    }

    runtime {
        docker: ""
        cpu: 2
        memory: "4 G"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}