import os
import yaml


def report_changes(config):
    import numpy as np
    from astropy.table import Table

    fcat_name = os.path.join(config['final_catalog_path'], config['final_catalog_name'])
    fcat = Table.read(fcat_name, format=config['final_catalog_format'])

    # Nsources 
    print(f"Nsources: {len(fcat)}")
    # N1d
    print(f"N_1d: {np.count_nonzero(fcat['exists_1d'])}")
    # verified
    fver = fcat[fcat['verified']==1]
    print(f"N verified: {len(fver)}")
    # Flags changed
    print(f"Flags changed: {np.count_nonzero(fver['updated_flag']!=fver['flag'])}")
    # redshift changed
    print(f"Redshifts changed: {np.count_nonzero(np.abs(fver['updated_zspec']-fver[config['zspec']])>5e-3)}")
    return

def merge_output(config):
    '''
    Merges verified_*fits file with inspecz_*fits file into final_*fits.
    '''
    from catalog_io import save_file
    from astropy.table import Table

    key_dict = { 'updated_zspec': 'updated_zspec',
                 'updated_flag': 'updated_flag',
                 'verified': 'verified'}

    
    fbase_name = os.path.join(config['inspecz_outpath'], config['inspecz_out_filename'])
    fnew_name = os.path.join(config['out_path'], config['out_filename'])
    outfilename = os.path.join(config['final_catalog_path'], config['final_catalog_name'])

    if os.path.exists(outfilename):
        fbase = Table.read(outfilename, format=config['final_catalog_format'])
    else:
        fbase = Table.read(fbase_name, format=config['inspecz_out_format'])
        
    fnew = Table.read(fnew_name, format=config['out_format'])

    save_file(fbase, fnew, key_dict, 'verified', outfilename, outformat=config['final_catalog_format'])
    return

if __name__ == '__main__':
    import sys
    import time

    try:
        yaml_file = open(sys.argv[1], 'r')
    except:
        yaml_file = open("config_files/example", 'r')
    
    config = yaml.load(yaml_file, Loader=yaml.FullLoader)

    merge_output(config)
    report_changes(config)
