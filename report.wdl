workflow ReportSingleCell10xMockWorkflow {
    File zipped_cellranger_analysis
    File zipped_scmatch_output
    String samplename
    String genome
    String git_repo_url
    String git_commit_hash
    String scmatch_hash
    String scmatch_url
    String cellranger_version

    call generate_report {
        input:
            zipped_cellranger_analysis = zipped_cellranger_analysis,
            zipped_scmatch_output = zipped_scmatch_output,
            samplename = samplename,
            genome = genome,
            git_repo_url = git_repo_url,
            git_commit_hash = git_commit_hash,
            scmatch_hash = scmatch_hash,
            scmatch_url = scmatch_url,
            cellranger_version = cellranger_version
}

task generate_report {
    File zipped_cellranger_analysis
    File zipped_scmatch_output
    
    String samplename
    String genome

    String git_repo_url
    String git_commit_hash
    String scmatch_hash
    String scmatch_url
    String cellranger_version

    # runtime commands
    Int disk_size = 200

    command {
        # Setup the cellranger data
        mkdir cellranger_data;
        tar xzf \
            ${zipped_cellranger_analysis} \
            -C cellranger_data \
            --strip-components 1;

        # Setup the scmatch output data
        mkdir scmatch_data;
        tar xzf ${zipped_scmatch_output} \
            -C scmatch_data \
            --strip-components 1;

        # Create the plots
        clusts=$(find ./cellranger_data/clustering/ -name "*.csv" | sort -V)
        python /opt/software/plotting.py \
            --scmatch ./scmatch_data/human_Spearman_top_ann.csv \
            --tsne ./cellranger_data/tsne/2_components/projection.csv \
            --clusters $clusts;

        # Generate the report
        kmeansclusts=$(ls *kmeans*_cluster.png | sort -V);
        #cellrangerversion=$(echo ${cellranger_version})
        python /opt/software/generate_report.py \
            --typing 1_celltype_to_tsne.png \
            --graph 2_celltype_to_knn_lmo_cluster.png \
            --kmeans $kmeansclusts \
            --genome "${genome}" \
            --scmatchhash "${scmatch_hash}" \
            --scmatch_url "${scmatch_url}" \
            --cellranger "${cellranger_version}" \
            --githash "${git_commit_hash}" \
            --gitrepo "${git_repo_url}" \
            -t /opt/report/report.md \
            -o completed_report.md;
        pandoc \
            -H /opt/report/report.css \
            -s ${samplename} \
            -o analysis_report.html;
        zip cluster_plots.zip *.png;
    }

    output {
        File report = "analysis_report.html"
        File zipped_plots = "cluster_plots.zip"
    }

    runtime {
        docker: "hsphqbrc/singlecell_10_unsupervised_labeling:1.0"
        cpu: 2
        memory: "4 G"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}