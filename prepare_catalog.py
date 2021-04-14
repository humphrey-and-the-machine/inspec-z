'''
This script
    a. maps the quality flags of a spectroscopic survey to a homogeneous system 0-4
    b. combines a spectroscopic catalog with a photometric redshift one (optional)
    c. saves the new catalog with additional columns needed for inscpez
Input: specz_catalog, photoz_catalog, configuration.yaml
Output: updated_specz_catalog
'''
import os
import yaml
import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.table import Table, join, join_skycoord, hstack
import matplotlib.pyplot as plt
import catalog_io as io
import tqdm

def replace_value(catalog, column, old_value, new_value):
    assert config['flagging_type'].lower() == 'vvds'
    '''
    VVDS-style flagging follows the system: (B)(A)d.x
    d: the quality of the spectrum (see Scodeggio2018, Garilli2014)
        Flag 1.X: tentative redshift measurement, with∼50% chance to be wrong
        Flag 2.X: still fairly secure,>95% confidence level.
        Flags 4.X and 3.X: highly secure redshift, with confidence>99%.
        Flag 9.X: redshift based a single emission feature, usually[OII]3727 Å. With the PDR-1 data we showed that the confidence level of this class is∼90%.
    The flag in the configuration file corresponds to "d"
    A=1 denotes the presence of broad lines
    B=2 or A>1: denotes that the spectrum was seredinitously detected in the slit
    .x: concordance with photoz; ignored in this mapping
    Examples:
    2.x: single object 
    34.x: Third object in slit with very secure redshift.
    219.x : Second object in slit, it has a single broad line.
    
    The old flag value is treated as a string. Split on the decimal point and consumed from left to right as an array.
    A new column is introduced to contain the broadline information, the secondary information is not retained.
    '''

    for i, flag in enumerate(column):
        
        if len(flag)>=1:
            if flag[-1] == str(old_value):
                catalog[config['new_flag_name']][i] = new_value
            if len(flag)>1:
                if flag[-2] == '1':
                    catalog[config['new_broadline_flag_name']][i] = 1
        elif len(flag) == 0:
            catalog[config['new_flag_name']][i] = -99

    pass

def convert_flags(catalog, config):
    catalog[config['new_flag_name']] = catalog[config['z_flag']]
    catalog[config['new_broadline_flag_name']] = [0]*len(catalog)

    # FUTURE: dymanic allocation from configuration file
    flags = [0, 1, 2, 3, 4, 5]

    if config['flagging_type'].lower() == 'sdss':
        catalog[config['new_flag_name']] = np.where(catalog[config['z_flag']] >= config['flag_upper_limit'], [1]*len(catalog), [4]*len(catalog))
        catalog[config['new_flag_name']] = np.where(catalog[config['z_flag']] <= config['flag_lower_limit'], [1]*len(catalog), catalog[config['new_flag_name']])

    elif config['flagging_type'].lower() == 'vvds':
        
        # convert existing flag column to string and ignore the decimal part
        flag_column = [str(m).split('.')[0] for m in catalog[config['z_flag']]]
        
        for flag in flags:
            
            if flag == 0:
                if config['0_limit'] == True:
                    catalog[config['new_flag_name']] = np.where(catalog[config['z_flag']] < config['flag_lower_limit'], [1]*len(catalog), catalog[config['new_flag_name']])
                
                
            # convert new flags to list
            if type(config[flag]) is not list:
                replace_flags = [config[flag]]
            else:
                replace_flags = config[flag]
            

            # map old to new value for each item in the list
            for temp_flag in replace_flags:

                replace_value(catalog, flag_column, temp_flag, flag)

    else:
        raise NotImplementedError(f"Flagging type {config['flagging_type']} is not implemented.")

    pass


############################################################################################


def prep_catalog(config):
    # zspec
    sp_filename = os.path.join(config['filename_path'], config['filename'])
    zspec_cat = Table.read(sp_filename, format=config['fileformat'])

    # redshift bounding box
    if config['coordinate_bounding_box']:
        zspec_cat = zspec_cat[ zspec_cat[config['RA']] >= float( config['ra_min'] ) ]
        zspec_cat = zspec_cat[ zspec_cat[config['RA']] <= float( config['ra_max'] ) ]
        zspec_cat = zspec_cat[ zspec_cat[config['DEC']] >= float( config['dec_min'] ) ]
        zspec_cat = zspec_cat[ zspec_cat[config['DEC']] <= float( config['dec_max'] ) ]

    # use boolean column for selection
    if config['use_boolean'] == True:
        zspec_cat = zspec_cat[ zspec_cat[config['selection']]==True ]

    # internal id for housekeeping
    zspec_cat['inspecz_id'] = np.arange(len(zspec_cat))

    # columns included in output
    zspec_columns = ['inspecz_id',
                    config['ID'],
                    config['RA'],
                    config['DEC'],
                    config['zspec'],
                    config['z_flag'],
                    config['1dname']]

    # keep extra columns
    zspec_columns = zspec_columns + config['keep_columns']

    zspec_cat.keep_columns(zspec_columns)

    # Map flags from survey to homogeneous system
    #FIXME: 
    # /home/sotiria/miniconda3/envs/ada/lib/python3.8/site-packages/numpy/ma/core.py:4071: 
    # FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison
    # check = compare(sdata, odata)
    print('Converting flags ... ', end='')
    convert_flags(zspec_cat, config)
    print('done.')

    # add column boolean for existing 1d spectra in specified location
    print('Searching for 1d ... ', end='')


    zspec_cat['exists_1d'] = [ (not filename1d.isspace()) and os.path.exists( os.path.join(config['1dpath'], filename1d.strip())) for filename1d in zspec_cat[config['1dname']]]
    """
    for item in zspec_cat[config['1dname']]:
        print(item,)
        print(len(item),)
        print(item.isspace())
        input()
    """
    print('done.')
    
    if config['zphot_match'] == True:
        # zspec
        # check if RA, DEC columns have units and assign correctly
        if zspec_cat[config['RA']].unit is None: 
            zspec_cat[config['RA']].unit = 'deg'
        
        if zspec_cat[config['DEC']].unit is None: 
            zspec_cat[config['DEC']].unit = 'deg'

        zspec_coo = SkyCoord(ra=zspec_cat[config['RA']], 
                           dec=zspec_cat[config['DEC']])
                
 
        # zphot
        print('Loading zphot catalog ... ', end="")
        
        ph_filename = os.path.join(config['zphot_path'], config['zphot_filename'])
        zphot_cat = Table.read(ph_filename, format=config['zphot_format'])
        
        print('done.')
        
        # check if RA, DEC columns have units assigned
        
        if zphot_cat[config['zphot_ra']].unit is None: 
            zphot_cat[config['zphot_ra']].unit = 'deg'
        
        if zphot_cat[config['zphot_dec']].unit is None: 
            zphot_cat[config['zphot_dec']].unit = 'deg'

        zphot_coo = SkyCoord(ra=zphot_cat[config['zphot_ra']], 
                            dec=zphot_cat[config['zphot_dec']])

        zphot_columns = [config['zphot_id'],
                        config['zphot_ra'],
                        config['zphot_dec'],
                        config['zphot']]

        zphot_cat.keep_columns(zphot_columns)
                            
        for col in zphot_columns:
            zphot_cat.rename_column(col, col+'_zphot')                            

        # matching zphot to zspec
        import time
        t1 = time.time()
        print('Matching catalogs ... ', end="")
        
        idx, d2d, d3d = zspec_coo.match_to_catalog_sky(zphot_coo, nthneighbor=1)

        zspec_cat['idx'] = idx
        zspec_cat['separation'] = d2d.to(u.arcsec)

        tmatch = hstack([zspec_cat, zphot_cat[idx]], join_type='outer')

        max_sep = 1.0 * u.arcsec
        my_mask = tmatch['separation'] > max_sep


        for column in zphot_cat.colnames:
            tmatch[column].mask = my_mask
            tmatch[column].fill_value = -99
        print('done.')
        print(f'Matching time: {round(time.time()-t1,2)} s')


        print('Saving output ...', end=" ")
        # astropy does not propage meta on column descriptions properly; removed for safety
        tmatch.meta = {}
        tmatch.write(os.path.join(config['inspecz_outpath'], config['inspecz_out_filename']),
                format=config['inspecz_out_format'],
                overwrite=config['inspecz_overwrite'])
        print('done.')
    else:
        print('Saving output ...', end=" ")
        # astropy does not propage meta on column descriptions properly; removed for safety
        zspec_cat.meta = {}
        zspec_cat.write(os.path.join(config['inspecz_outpath'], config['inspecz_out_filename']),
                format=config['inspecz_out_format'],
                overwrite=config['inspecz_overwrite'])
        print('done.')

    print(f"Output in { os.path.join(config['inspecz_outpath'], config['inspecz_out_filename']) }")
    return

if __name__ == '__main__':
    import sys
    import time

    try:
        yaml_file = open(sys.argv[1], 'r')
    except:
        yaml_file = open("config_files/example.yaml", 'r')
    
    config = yaml.load(yaml_file, Loader=yaml.FullLoader)

    t0 = time.time()
    prep_catalog(config)
    print(f'Catalog prep done in: {round(time.time()-t0,2)} s')
