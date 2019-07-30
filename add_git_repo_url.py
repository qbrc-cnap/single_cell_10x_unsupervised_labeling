def add_to_context(request, workflow_obj, context_dict, context_args):
    '''
    Here we add the git repository URL to the context.  This lets us
    put the repository url into reports, etc.

    Here we are adding a hidden input.  The context_args dict has a key named
    "variable_name", which gives us the name of the variable to fill-in in the HTML
    template when the view is requested
    '''
    var_name = context_args['variable_name']
    context_dict[var_name] = workflow_obj.git_url
