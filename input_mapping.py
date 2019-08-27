#! /usr/bin/python3

from base.models import Resource
import os

def map_inputs(user, all_data, data_name, id_list):
    '''
    `user` is a User instance (or subclass).  This gives us
    the option of applying user-specific logic to the mapping.
    Since the code that calls this function does NOT know
    the structure of the input data, it cannot impose any logic
    such as filtering Resource objects for a particular user.
    Therefore we have to keep that information here

    `unmapped_data` is some data structure sent by
    the frontend.  The structure is known to the 
    developer since they specified the input element responsible
    for creating the data.  For example, a file chooser will send
    a list/array of primary keys.

    `id_list` is a list of WDL input "names"/ids that we are mapping
    to.  Note that the ordering is important.  Make sure the logic below
    matches the order in gui.json 

    '''
    unmapped_data = all_data[data_name]
    input_suffix = '.tar.gz'
    # Pull all the uploaded files that end with above suffix.
    #for pk in unmapped_data:
    pk = unmapped_data # as it is no longer an integer
    r = Resource.objects.get(pk=pk)
    input_path = None
    if (r.owner == user) or (user.is_staff):
        if r.path.endswith(input_suffix):
            input_path = r.path
        else:
            print('Skipping %s' % r.path)
    else:
        raise Exception('The user %s is not the owner of Resource with primary key %s.' % (user, pk))
    
    # now we have a list of files that had the correct naming scheme.

    #input_samples = [os.path.basename(x)[ : -len(input_suffix)]
    #                 for x in input_path_list]
    #sample_dict = dict(zip(input_samples, input_path_list))
    if not input_path:
        raise Exception('The file %s does not have an appropriate suffix, but somehow bypassed gui.json regex' % r)
    else:
        return {id_list[0] : input_path}
    # Unsure if I need second key-pair to be returned
    #return {id_list[0]:final_r1_list, id_list[1]:final_r2_list}
