workflow CellrangerSingleCellMockWorkflow {
    File zipped_fastqs
    File zipped_reference
    String samplename

    call cellranger_count {
        input:
            zipped_fastqs = zipped_fastqs,
            zipped_reference = zipped_reference,
            samplename = samplename
    }
    
    call cellranger_version {}
}

task cellranger_count {
    File zipped_fastqs
    File zipped_reference
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
            --fastqs=./fastqs;

        # Moved web summary to pwd for simpler / safer export
        mv ./${samplename}/outs/web_summary.html .;

        # Package analysis directory for export.
        tar czf \
            ${samplename}_cellranger_analysis.tar.gz \
            --directory=./${samplename}/outs/ \
            analysis;
        
        # Package raw and filtered matrices directories for export
        # Also moved the hdf5 for separate export from CSVs
        #   and simpler / safer WDL output
        mv ./${samplename}/outs/raw_feature_bc_matrix.h5 .;
        tar czf \
            ${samplename}_cellranger_raw_csv.tar.gz \
            --directory=./${samplename}/outs/ \
            raw_feature_bc_matrix;
        
        mv ./${samplename}/outs/filtered_feature_bc_matrix.h5 .;
        tar czf \
            ${samplename}_cellranger_filtered_csv.tar.gz \
            --directory=./${samplename}/outs/ \
            filtered_feature_bc_matrix;
        
        # Move BAM, BAM index, and cloupe file to pwd for simpler WDL output
        mv ./${samplename}/outs/possorted_genome_bam.bam .;
        mv ./${samplename}/outs/possorted_genome_bam.bam.bai .;
        mv ./${samplename}/outs/cloupe.cloupe .;
    }

    output {
        File cellranger_qc_summary = "web_summary.html"
        File zipped_cellranger_analysis = "${samplename}_cellranger_analysis.tar.gz"
        File zipped_cellranger_raw_csv = "${samplename}_cellranger_raw_csv.tar.gz"
        File zipped_cellranger_filtered_csv = "${samplename}_cellranger_filtered_csv.tar.gz"
        File cellranger_raw_hdf5 = "raw_feature_bc_matrix.h5"
        File cellranger_filtered_hdf5 = "filtered_feature_bc_matrix.h5"
        File cellranger_bam = "possorted_genome_bam.bam"
        File cellranger_bam_index = "possorted_genome_bam.bam.bai"
        File cellranger_cloupe = "cloupe.cloupe"
    }

    runtime {
        docker: "docker.io/hsphqbrc/cellranger:3.1.0"
        cpu: 32
        memory: "100 GB"
        disks: "local-disk " + disk_size + " HDD"
        bootDiskSizeGb: 20
        preemptible: 0
    }
}

task cellranger_version {
    # runtime commands
    Int disk_size = 20

    command {
        /opt/software/cellranger/cellranger | head -2 | tail -1
    }

    output {
        String version = read_string(stdout())
    }

    runtime {
        docker: "docker.io/hsphqbrc/cellranger:3.1.0"
        cpu: 2
        memory: "2 GB"
        disks: "local-disk " + disk_size + " HDD"
        bootDiskSizeGb: 20
        preemptible: 0
    }
}

task cellranger_convert_to_excel {
    File zipped_cellranger_analysis
    String samplename

    # runtime commands
    Int disk_size = 40

    command {
        # Setup the cellranger data
        mkdir cellranger_data;
        tar xzf \
            ${zipped_cellranger_analysis} \
            -C cellranger_data \
            --strip-components 1;
        # convert to excel
        # Pass as input a find of all CSVs in the diffexp directory
        # Sort for natural sort, so sheets are in sensible order
        python3 /opt/software/convert_to_excel.py \
            -o ${samplename}.differential_expressions.xlsx \
            $(find ./cellranger_data/diffexp -name "*.csv" | sort -V);
    }

    output {
        File excel_diffexp = "${samplename}.differential_expressions.xlsx"
    }

    runtime {
        docker: "docker.io/hsphqbrc/singlecell_10_unsupervised_labeling:1.0"
        cpu: 2
        memory: "2 GB"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}