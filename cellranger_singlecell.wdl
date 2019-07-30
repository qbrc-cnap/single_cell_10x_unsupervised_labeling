workflow CellrangerSingleCellMockWorkflow {
    File zipped_fastqs
    File zipped_reference
    String num_expected_cells
    String samplename

    call cellranger_count {
        input:
            zipped_fastqs = zipped_fastqs,
            zipped_reference = zipped_reference,
            num_expected_cells = num_expected_cells,
            samplename = samplename
    }
    
    call cellranger_version {}
}

task cellranger_count {
    File zipped_fastqs
    File zipped_reference
    String num_expected_cells
    String samplename

    # runtime commands
    Int disk_size = 1000

    command {
        mkdir fastqs;
        tar xzf ${zipped_fastqs} -C fastqs --strip-components 1;
        mkdir ref;
        tar xzf ${zipped_reference} -C ref --strip-components 1;
        /opt/software/cellranger/cellranger count \
            --id=${samplename} \
            --transcriptome=./ref \
            --fastqs=./fastqs \
            --expect-cells=${num_expected_cells};
        tar czf ${samplename}_cellranger.tar.gz ./${samplename}
    }

    output {
        File zipped_cellranger_output = "${samplename}_cellranger.tar.gz"
    }

    runtime {

    }
}

task cellranger_version {
    # runtime commands
    Int disk_size = 10

    command {
        version=$(/opt/software/cellranger/cellranger | head -2 | tail -1)
    }

    output {
        String cellranger_version = "${version}"
    }

    runtime {

    }
}