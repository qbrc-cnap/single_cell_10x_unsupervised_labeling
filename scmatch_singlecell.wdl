workflow ScmatchSingleCellMockWorkflow {

}

task scmatch_celltype {
    File zipped_cellrange_output
    File zipped_reference
    String species

    # runtime commands
    Int disk_size = 

    command {
        mkdir ref;
        tar xzf ${zipped_reference} -C ref --strip-components 1;
        mkdir data;
        tar xzf ${zipped_cellrange_output} -C data --strip-components 1;
        python /opt/software/scMatch/scMatch.py \
            --coreNum 8 \
            --refType ${species} \
            --testType ${species} \
            --refDS ./ref \
            --dFormat 10x \
            --testDS ./data/outs/filtered_feature_bc_matrix \
            --keepZeros n;
        tar czf \
            ${samplename}_scMatch.tar.gz \
            --directory=./data/outs/filtered_feature_bc_matrix/ \
            annotation_result_keep_expressed_genes;
    }

    output {
        File zipped_scmatch_output = "${samplename}_scMatch.tar.gz"
    }

    runtime {
        docker: ""
        cpu: 8
        memory: "6 GB"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}