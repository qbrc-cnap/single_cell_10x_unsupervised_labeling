workflow ReportSingleCell10xMockWorkflow {

}

task generate_report {
    File zipped_cellranger_analysis
    File zipped_scmatch_output

    # runtime commands
    Int disk_size = 200

    command {
        # Setup the cellranger data
        mkdir cellranger_data;
        tar xzf \
            ${zipped_cellranger_analysis} \
            -C cellranger_data \
            --strip-components 1;
        tar xzf ${zipped_cellranger_output} -C cellranger_data --strip-components 1;

        # Setup the scmatch output data
        mkdir scmatch_data;
        tar xzf ${zipped_scmatch_output} -C scmatch_data --strip-components 1;

        # Create the plots
        clusts=$(find ./cellranger_data/clustering/ -name "*.csv" | sort -V)
        python /opt/software/plotting.py \
            --scmatch ./scmatch_data/human_Spearman_top_ann.csv \
            --tsne ./cellranger_data/tsne/2_components/projection.csv \
            --clusters ${clusts};

        # Generate the report
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