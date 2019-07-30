import "cellranger_singlecell.wdl" as cellranger_singlecell

workflow SingleCell10xUnsupervisedWorkflow {
    # This workflow is a 'super' workflow

    File zipped_fastqs
    File zipped_reference

    call cellraner_singlecell.cellranger_count as count {
        input:
            zipped_fastqs = zipped_fastqs,
            zipped_reference = zipped_reference
    }
}