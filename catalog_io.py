import os
import yaml
import numpy as np
from astropy.table import Table

def check_buffer_version(buffer_yaml, config):
    
    if not set(buffer_yaml.keys()).issubset(set(config.keys())):
        return 0

    for key, value in buffer_yaml.items():
        if config[key] != buffer_yaml[key]:
            return 0
    
    return 1

def create_output_catalog(config):
    
    # Read inspecz table
    filename = os.path.join(config['inspecz_outpath'], config['inspecz_out_filename'])
    fileformat = config['inspecz_out_format']
    f = Table.read(filename, format=fileformat)

    # add mandatory columns
    # Read final table, if exists
    final_filename = os.path.join(config['final_catalog_path'], config['final_catalog_name'])
    final_fileformat = config['final_catalog_format']
    if os.path.exists(final_filename):
        final_f = Table.read(final_filename, format=final_fileformat)
        final_zspec = final_f['updated_zspec']
        final_flag = final_f['updated_flag']
        final_verified = final_f['verified']
    else:
        final_zspec = f[config['zspec']]
        final_flag = [-1]*len(f)
        final_verified = [0]*len(f)
    

    # if the source has been inspected and saved in the config['final_catalog_name'] file, then use updated_zspec, flag and verified status
    f['updated_zspec'] = np.where(final_verified==1, final_zspec, f[config['zspec']])
    f['updated_flag'] = np.where(final_verified==1, final_flag, [-1]*len(f))
    f['verified'] = np.where(final_verified==1, final_verified, [0]*len(f))

    # save
    outfilename = os.path.join(config['out_path'], config['out_filename'])
    f.write(outfilename, overwrite=True, format=config['out_format'])

    return f

def get_catalog(config):

    mode = config['vstatus']
    
    input_filename = os.path.join(config['inspecz_outpath'], config['inspecz_out_filename'])
    resume_filename = os.path.join(config['out_path'], config['out_filename'])

    if mode == 'new' and not os.path.exists( input_filename ):
        raise ValueError(f"File \'{input_filename}\' does not exist.")
    elif mode == 'resume' and not os.path.exists( resume_filename ):
        mode = 'new'
    
    # read in catalog
    if mode == 'new':
        fin = create_output_catalog(config)
           
    elif mode == 'resume':
        fin = Table.read(resume_filename, format=config['out_format'])
    
    else:
        raise ValueError(f"Mode \'{mode}\' not a valid option. Use \'new\' or \'resume\'.")
    
    # sample selection
    fcat = select_sample(fin, config)

    if len(fcat)==0:
        print(f'No sources match sample selection!')
        exit()
    else:
        print(f'Inspecting {len(fcat)} sources.')

    return fcat

def select_sample(fcat, config):
    import numpy as np
    # select only sources with 1D available
    fcat = fcat[fcat['exists_1d']]

    # select only verified sources
    if config['view_verified']==True:
        
        if 'verified' in fcat.keys():
            fin = fcat[fcat['verified']==1]
            
            if len(fin)==0:
                raise Exception('No verified sources found.')
                
    # select only non - verified sources                
    elif config['view_verified']==False:

        if 'verified' in fcat.keys():
            fin = fcat[fcat['verified']!=1]
            
            if len(fin)==0:
                raise Exception('No non-verified sources found.')

    # view all regardless of verified status
    else:
        fin = fcat

    # select specz redshift range
    f_zmin = fin[fin[config['zspec']] >= float(config['vzmin'])]
    f_zmax = f_zmin[f_zmin[config['zspec']] <= float(config['vzmax'])]
    
    if config['vzphot_outlier'].lower() == 'ignore':
        f_out = f_zmax
    elif config['vzphot_outlier'].lower() in ['outlier', 'inlier', 'none']:
        Dz_out = np.abs(f_zmax[config['zspec']]-f_zmax[config['zphot']+'_zphot'])/(1+f_zmax[config['zspec']])

        if config['vzphot_outlier'].lower() == 'outlier':   
            f_zphot = f_zmax[Dz_out>0.15]
        if config['vzphot_outlier'].lower() == 'inlier':
            f_zphot = f_zmax[Dz_out<=0.15]
        if config['vzphot_outlier'].lower() == 'none':
            f_zphot = f_zmax[np.abs(Dz_out) > 7]
        f_out = f_zphot
    else:
        raise ValueError(f"Value zphot_out: {config['vzphot_outlier']} if not a valid choice.")

    # TODO
    # select quality flags
    if len(config['vquality']) == 0:
        print(f'Configuration parameter \'vquality\' is empty, using all available flags.')
        
    else:

        mask = [False]*len(f_out)
        for fflag in config['vquality']:

            mask = np.where(f_out[config['new_flag_name']].astype(int)==int(fflag), [True]*len(f_out), mask)

        f_out = f_out[mask]


    
    # sampling of catalog, random selection of vsample
    fraction = int( len(f_out)*config['vsample_percent']/100 )
    if fraction == len(f_out):
        return f_out
    elif fraction<1:
        raise ValueError(f'Requested sample is smaller than the size of the catalog!')
    elif fraction == 1:
        return f_out
    else:
        # add column for indexing
        # parameter vseed fixes the random sampling for debugging and reproducibility
        if config['vseed'] is not None:
            np.random.seed(config['vseed'])

        f_out['_index_'] = np.array(range(0, len(f_out)))

        f_out.add_index('_index_')

        # Random selection of N=fraction sources from f_out, without replacement
        choice = np.random.choice(f_out['_index_'], replace=False, size=fraction)

        sample = f_out.loc[choice]

        return sample

def read_1d(file, style):
    '''
    Wrapper function for reading various 1d file profiles
    '''
    import sp1d_profiles as sp1d
    if style.lower() == 'sdss':
        wave, flux, mask, error = sp1d.read_sdss_1d(file)
    elif style.lower() == 'cesam':
        wave, flux, mask, error = sp1d.read_cesame_1d(file)
    elif style.lower() == 'vipers-pdr2':
        wave, flux, mask, error = sp1d.read_VIPERS_PDR2_1d(file)
    elif style.lower() == 'gama':
        wave, flux, mask, error = sp1d.read_GAMA_1d(file)
    elif style.lower() == 'vvds':
        wave, flux, mask, error = sp1d.read_VVDS_1d(file)      
    elif style.lower() == 'zcosmos':
        wave, flux, mask, error = sp1d.read_zCOSMOS_1d(file)     
    else:
        raise NotImplementedError(f'Profile {style} not implemented. Please add handler in catalog_io.')    
    return wave, flux, mask, error

def save_1d_MEF(catalog, config):
    from astropy.io import fits
    from tqdm.contrib import tenumerate
    hdu_MEF_list = fits.HDUList()

    for i, file_1d in tenumerate(range(0, len(catalog))):
        file_1d = catalog[config['1dname']][i]
        fin_1d = os.path.join( config['1dpath'], file_1d)
        
        try:
            wave, flux, mask, error = read_1d(fin_1d, config['1dsp_profile'])    
        except:
            wave, flux, mask, error = [0], [0], [0], [0]
        w1d = fits.Column(name='wave1d', format='E', array=wave)
        f1d = fits.Column(name='flux1d', format='E', array=flux)
        m1d = fits.Column(name='mask1d', format='E', array=mask)
        e1d = fits.Column(name='error1d', format='E', array=error)

        hdu = fits.BinTableHDU.from_columns([w1d, f1d, m1d, e1d])
        
        hdu_MEF_list.append(hdu)

    hdu_MEF_list.writeto(config['out_1d_MEF_name'], overwrite=True)
    pass    

def save_file(fcat, file_, key_dict, column_selection, outfilename, outformat='fits'):

    fcat.add_index('inspecz_id')
    file_.add_index('inspecz_id')

    for key in key_dict.keys():
        if key not in fcat.colnames:
            fcat[key] = [-99]*len(fcat)

    for file_row in file_:
        if file_row[column_selection]==1:
            id_ = file_row['inspecz_id']
            # find row in fcat
            fcat_row = fcat.loc['inspecz_id', id_]
            
            # substite in fcat
            for key, value in key_dict.items():
                fcat_row[key] = file_row[value]
        
    # save file to disk
    fcat.write(outfilename, overwrite=True, format=outformat)
    print(f'Catalog saved in {outfilename}')
    return


if __name__ == '__main__':
    import os
    import matplotlib.pyplot as plt
    from verify import Verify

    plt.rcParams['figure.autolayout'] = False

    # configuration
    yaml_file = open("config_files/example.yaml", 'r')
    config = yaml.load(yaml_file, Loader=yaml.FullLoader)

    fcat = get_catalog(config)

    s1 = Verify(fcat, config)
    s1.verify(show=True)

