import "cellranger_singlecell.wdl" as cellranger_singlecell
import "scmatch_singlecell.wdl" as scmatch_singlecell
import "report.wdl" as reporting

workflow SingleCell10xUnsupervisedWorkflow {
    # This workflow is a 'super' workflow

    File zipped_fastqs
    File zipped_cellranger_reference
    File zipped_scmatch_reference

    String num_expected_cells
    String samplename
    String species

    String output_zip_name

    String genome
    String git_repo_url
    String git_commit_hash

    call cellranger_singlecell.cellranger_count as count {
        input:
            zipped_fastqs = zipped_fastqs,
            zipped_reference = zipped_cellranger_reference
    }

    call cellranger_singlecell.cellranger_version as cellranger_version {}

    call scmatch_singlecell.scmatch_celltype as celltype {
        input:
            zipped_cellranger_filtered_csv = count.zipped_cellranger_filtered_csv,
            zipped_reference = zipped_scmatch_reference,
            species = species
    }

    call reporting.generate_report {
        input:
            zipped_cellranger_analysis = count.zipped_cellranger_analysis,
            zipped_scmatch_output = celltype.zipped_scmatch_reference
    }

    output {

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
}