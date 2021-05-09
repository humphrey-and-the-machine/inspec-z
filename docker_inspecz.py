def inspecz(config):
    import os
    import sys
    from catalog_io import get_catalog, select_sample, check_buffer_version
    from verify import Verify

    '''
        The interactive version of inspecz allows the deletions of previous buffer files, 
        after ther the selection of the sample has been changed in the configuration file.

        This script is adjusted to work within a docker container:
            1. no interactive messages in the command line
            2. verifies the consistency of the buffer and configuration files
            3. inspection parameter 'vstatus' is always _resume_
        In order to start a new sample selection, the buffer_* files must be removed manually.
    '''

    print(f"Sample selection:")
    print(f"-verified: {config['view_verified']}")
    print(f"-zphot state: {config['vzphot_outlier']}")
    print(f"-redshift range: {config['vzmin']}<z<{config['vzmax']}")
    print(f"-sampling: {config['vsample_percent']}%")

    # resume always on for Docker version
    config['vstatus']=='resume'

    
    buffer_name = os.path.join(config['buffer_path'], config['buffer_name'])
    buffer_config_name = '.'.join(buffer_name.split('.')[:-1])+'.yaml'

    if config['vstatus']=='resume':
        if os.path.exists( buffer_name ):

            # Check for consistency between input and buffer selection, if exists
            if os.path.exists( buffer_config_name ):
                with open(buffer_config_name,'r') as fin:
                    buffer_config = yaml.load(fin, Loader=yaml.FullLoader)
                    # ignore vstatus=new/resume from buffer config file during consistency check
                    buffer_config.pop('vstatus')

                resp = check_buffer_version(buffer_config, config)
            
                if resp == 0 :
                    raise ValueError(f'Inconsistent input and buffer files. Remove previous buffer file:\n{buffer_config_name}')
            
            # If verified buffer exists, resume from buffer
            remove = 'r'
            if remove.lower() == 'd':
                os.remove(buffer_name)
                print(f'Removed {buffer_name}.\nStarting from scratch.\n')
            elif remove.lower() == 'r':
                print(f'Resuming from {buffer_name}')
                pass
            elif remove.lower() == 'a':
                exit(f"aborted.")
            else:
                raise ValueError(f'Invalid selection, start again.')
    elif config['vstatus']=='new':
        if os.path.exists( buffer_name ):
            ans = input(f"Delete {buffer_name}? Y/N\n")
            if ans.lower() == "y":
                os.remove(buffer_name)
            else:
                exit("Aborted.")
    else:
        raise ValueError(f"{config['vstatus']} not a valid option. Use \'resume\'")
    fcat = get_catalog(config)
    s1 = Verify(fcat, config)
    s1.verify(show=True)

if __name__ == '__main__':
    import sys
    import time
    import yaml

    try:
        yaml_file = open(sys.argv[1], 'r')
    except:
        yaml_file = open("config_files/dockerConfig.yaml", 'r')

    config = yaml.load(yaml_file, Loader=yaml.FullLoader)


    inspecz(config)
