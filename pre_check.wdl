workflow  SingleCell10xUnsupervisedWorkflow {
    File zipped_fastqs
    File zipped_cellranger_reference
    File zipped_scmatch_reference

    String samplename
    String species

    String output_zip_name

    String genome
    String git_repo_url
    String git_commit_hash
}

task assert_valid_fastq {
    File zipped_fastqs

    # runtime commands
    Int disk_size = 200

    command {
        # Untar fastqs to generic directory
        mkdir fastqs;
        tar xzf ${zipped_fastqs} -C fastqs --strip-components 1;
        # Perform pre-check on all FASTQs
        python3 /opt/software/perform_precheck.py \
            -i $(find fastqs -name "*_R*") \
            -f $(find fastqs -name "*_I*");
    }
    
    runtime {
        docker: ""
        cpu: 4
        memory: "50 G"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}