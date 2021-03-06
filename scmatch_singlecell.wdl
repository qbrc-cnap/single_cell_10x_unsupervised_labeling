workflow ScmatchSingleCellMockWorkflow {
    File zipped_cellranger_filtered_csv
    File zipped_reference
    String species

    call scmatch_celltype {
        input:
            zipped_cellranger_filtered_csv = zipped_cellranger_filtered_csv,
            zipped_reference = zipped_reference,
            species = species
    }

    #call scmatch_version {}
    call repo_url {}
    call commit_hash {}

}

task scmatch_celltype {
    File zipped_cellranger_filtered_csv
    File zipped_reference
    String species
    String samplename

    # runtime commands
    Int disk_size = 500

    command <<<
        mkdir ref;
        tar xzf ${zipped_reference} -C ref --strip-components 1;
        mkdir filtered_feature_bc_matrix;
        tar xzf ${zipped_cellranger_filtered_csv} \
            -C filtered_feature_bc_matrix \
            --strip-components 1;
        #gzip -d ./filtered_feature_bc_matrix/*.gz;
        find ./filtered_feature_bc_matrix -name "*.gz" -exec gzip -d {} \;
        python /opt/software/scMatch/scMatch.py \
            --coreNum 4 \
            --refType ${species} \
            --testType ${species} \
            --refDS ./ref \
            --dFormat 10x \
            --testDS ./filtered_feature_bc_matrix \
            --keepZeros n;
        tar czf \
            ${samplename}_scMatch.tar.gz \
            --directory=./filtered_feature_bc_matrix/ \
            annotation_result_keep_expressed_genes;
    >>>

    output {
        File zipped_scmatch_output = "${samplename}_scMatch.tar.gz"
    }

    runtime {
        docker: "docker.io/hsphqbrc/singlecell_10_unsupervised_labeling:1.0"
        cpu: 8
        memory: "24 GB"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}

task commit_hash {
    # runtime commands
    Int disk_size = 20

    command {
        cat /opt/software/scMatch/git_commit_hash
    }

    output {
        String git_commit_hash = read_string(stdout())
    }

    runtime {
        docker: "docker.io/hsphqbrc/singlecell_10_unsupervised_labeling:1.0"
        cpu: 1
        memory: "1 GB"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}

task repo_url {
    # runtime commands
    Int disk_size = 20

    command {
        cat /opt/software/scMatch/git_repo_url
    }

    output {
        String git_repo_url = read_string(stdout())
    }

    runtime {
        docker: "docker.io/hsphqbrc/singlecell_10_unsupervised_labeling:1.0"
        cpu: 1
        memory: "1 GB"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}