def read_sdss_1d(file):
    from astropy.io import fits
    import numpy as np
    with fits.open(file,memmap=False) as f:
        # Info
        try:
            Units = f[0].header['BUNIT']
        except:
            Units = ""
        try:
            FrameID = f[0].header['FRAMEID']
        except:
            FrameID = ""
        try:
            Observatory = f[0].header['OBSERVAT']
        except:
            Observatory = ""
        try:
            Object = f[0].header['OBJECT']
        except:
            Object = ""
        #
        # Reconstruct spectrum
        try:
            # sdss format
            data = f[1].data
            wave = np.power(10.0, data.field('loglam'))
            flux = data.field('flux') 
            # TODO
            error = []
            # TODO
            mask = []
        except:
            # apogee format
            Npixels = f[1].header['NAXIS1']
            wave_min = f[1].header['CRVAL1']
            wave_step = f[1].header['CDELT1']
            wave = 10. ** np.arange(wave_min, wave_min + Npixels * wave_step, wave_step)

            flux = f[1].data[0]
            error = f[2].data[0]
            mask = f[3].data[0]

    return wave, flux, error, mask

def read_cesame_1d(file):
    from astropy.io import fits
    import numpy as np
    #
    with fits.open(file, memmap=False ) as f:
        #
        Npixels = f[0].header['NAXIS1']
        wave_min = f[0].header['CRVAL1']
        wave_step = f[0].header['CDELT1']
        #wave = np.arange(wave_min, wave_min+wave_step*Npixels, wave_step)
        wave = ((np.arange(Npixels) + 1.0) - f[0].header['CRPIX1'])*f[0].header['CDELT1'] + f[0].header['CRVAL1']
        #
        if f[0].header['NAXIS']==1:
            flux = f[0].data
        else:
            flux = np.ravel(f[0].data[0,:]).T
    # TODO
    error = []
    # TODO
    mask = []
    #
    return wave, flux, error, mask

def read_GAMA_1d(file):
    from astropy.io import fits
    import numpy as np
    #
    with fits.open(file, memmap=False ) as f:
        N = f[0].header['NAXIS1']
        wave = ((np.arange(N) + 1.0) - f[0].header['CRPIX1'])*f[0].header['CD1_1'] + f[0].header[' CRVAL1']
        flux = f[0].data[0]
        error = f[0].data[1]
        mask = []
    return wave, flux, error, mask

def read_VIPERS_PDR2_1d(file):
    from astropy.io import fits
    import numpy as np
    #

    with fits.open(file.strip(), memmap=False ) as f:
        wave = np.array([f[1].data[w][0] for w in range(0,len(f[1].data))])
        flux = np.array([f[1].data[w][1] for w in range(0,len(f[1].data))])
        error = np.array([f[1].data[w][2] for w in range(0,len(f[1].data))])
        mask = np.array([f[1].data[w][5] for w in range(0,len(f[1].data))])
    return wave, flux, error, mask
    '''
    CRPIX1  =                    1 / Reference pixel in axis1
    CRVAL1  =                    1 / Physical value of the reference pixel
    CDELT1  =                    1 / Size projected into a detector pixel in axis1

    CRVAL1  =                5500.                                                  
    CRPIX1  =                  -1.                                                  
    CDELT1  =      7.1399998664856                                                  
    '''

def read_VVDS_1d(file):    
    # FIXME same as cesam style, remove from here and edit VVDS deep/udeep config files
    from astropy.io import fits
    import numpy as np
    #
    with fits.open(file, memmap=False ) as f:
        #
        Npixels = f[0].header['NAXIS1']
        wave_min = f[0].header['CRVAL1']
        wave_step = f[0].header['CDELT1']
        wave = ((np.arange(Npixels) + 1.0) - f[0].header['CRPIX1'])*f[0].header['CDELT1'] + f[0].header['CRVAL1']
        #wave = np.arange(wave_min, wave_min+wave_step*Npixels, wave_step)
        #
        if f[0].header['NAXIS']==1:
            flux = f[0].data
        else:
            flux = np.ravel(f[0].data[0,:]).T
        # TODO
        error = []
        # TODO
        mask = []

    return wave, flux, error, mask
    
def read_zCOSMOS_1d(file):    
    from astropy.io import fits
    import numpy as np
    #
    with fits.open(file, memmap=False ) as f:
        wave = f[1].data[0][0]
        flux = f[1].data[0][1]
        # TODO
        error = f[1].data[0][2]
        # TODO
        mask = []

    return wave, flux, error, mask
    
