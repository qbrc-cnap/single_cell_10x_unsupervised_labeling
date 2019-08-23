import "cellranger_singlecell.wdl" as cellranger_singlecell
import "scmatch_singlecell.wdl" as scmatch_singlecell
import "report.wdl" as reporting

workflow SingleCell10xUnsupervisedWorkflow {
    # This workflow is a 'super' workflow

    File zipped_fastqs
    File zipped_cellranger_reference
    File zipped_scmatch_reference

    String samplename
    String species

    String output_zip_name

    String genome
    String git_repo_url
    String git_commit_hash

    call cellranger_singlecell.cellranger_count as count {
        input:
            zipped_fastqs = zipped_fastqs,
            zipped_reference = zipped_cellranger_reference,
            samplename = samplename
    }

    call cellranger_singlecell.cellranger_convert_to_excel as convert_to_excel {
        input:
            zipped_cellranger_analysis = count.zipped_cellranger_analysis,
            samplename = samplename
    }

    call cellranger_singlecell.cellranger_version as cellranger_get_version {}

    call scmatch_singlecell.scmatch_celltype as celltype {
        input:
            zipped_cellranger_filtered_csv = count.zipped_cellranger_filtered_csv,
            zipped_reference = zipped_scmatch_reference,
            species = species,
            samplename = samplename
    }

    #call scmatch_singlecell.scmatch_version as scmatch_version {}
    call scmatch_singlecell.commit_hash as scmatch_commit_hash{}

    call scmatch_singlecell.repo_url as scmatch_repo_url {}

    call reporting.generate_report as report_gen {
        input:
            zipped_cellranger_analysis = count.zipped_cellranger_analysis,
            zipped_scmatch_output = celltype.zipped_scmatch_output,
            samplename = samplename,
            genome = genome,
            git_repo_url = git_repo_url,
            git_commit_hash = git_commit_hash,
            scmatch_hash = scmatch_commit_hash.git_commit_hash,
            scmatch_url = scmatch_repo_url.git_repo_url,
            cellranger_version = cellranger_get_version.version
    }

    call collate_outputs {
        input:
            cellranger_qc_report = count.cellranger_qc_summary,
            report = report_gen.report,
            plots = report_gen.zipped_plots,
            diffexp_xlsx = convert_to_excel.excel_diffexp,
            raw_counts = count.zipped_cellranger_raw_csv,
            filtered_counts = count.zipped_cellranger_filtered_csv,
            output_zip_name = output_zip_name
    }

    output {
        collate_outputs.zipped_output
    }

    meta {
        workflow_title: "10x single cell typing and differential expression."
        workflow_short_description: "A pipeline for 10x single cell typing; and differential expression of unsupervised clusters and background."
        workflow_long_description: "Use this workflow for aligning 10x sequencing output, barcode assignment, gene expression normalization, unsupervised clustering, and differential expression against background for each cluster with 10x's Cellranger software. The cell typing is done with scMatch."
    }
}

task collate_outputs {
    File cellranger_qc_report
    File report
    File plots
    File diffexp_xlsx
    File raw_counts
    File filtered_counts
    String output_zip_name

    # runtime commands
    Int disk_size = 100
    
    command {
        zip ${output_zip_name}.zip \
            ${cellranger_qc_report} \
            ${report} \
            ${plots} \
            ${diffexp_xlsx} \
            ${raw_counts} \
            ${filtered_counts}
    }

    output {
        File zipped_output = "${output_zip_name}.single_cell_10x.zip"
    }

    runtime {
        docker: "docker.io/hsphqbrc/singlecell_10_unsupervised_labeling:1.0"
        cpu: 2
        memory: "2 GB"
        disks: "local-disk " + disk_size + " HDD"
        preemptible: 0
    }
}