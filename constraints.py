import json
import analysis.models
from analysis.models import AnalysisProject, ProjectConstraint

def check_constraints(implemented_constraint, inputs_json_path):
    '''
    For this workflow, we can impose a constraint on the number of samples we will
    allow for processing.

    The length of the SingleCell10xUnsupervisedWorkflow.zipped_fastqs key will be used as the
    determinant of that number
    '''

    # load the inputs json:
    j = json.load(open(inputs_json_path))
    try:
        fastq_list = j['SingleCell10xUnsupervisedWorkflow.zipped_fastqs']
        
    except KeyError:
        # The chances of reaching this are very unlikely, but we are being extra careful here
        print('This should not happen-- the SingleCell10xUnsupervisedWorkflow.zipped_fastqs key should be present in your inputs JSON file')
        return False

    # implemented_constraint is of type ImplementedConstraint and represents the base class for the actual constraint types
    # which hold the *value* of the constraint.  Since we know we are applying an AnalysisUnitConstraint, we can access it
    # with the lower-case name as below.
    constraint_value = implemented_constraint.analysisunitconstraint.value

    # finally we can check if the constraints are satisfied:
    constraint_satisfied = len(fastq_list) <= (constraint_value * 2)

    message = ''
    if not constraint_satisfied:
        message = '%d paired fastq files were submitted for analysis, but only a maximum of %d are permitted.' % (len(fastq_list), constraint_value * 2)

    return (constraint_satisfied, message)
