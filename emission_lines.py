import matplotlib.pyplot as plt

def plot_lines(ax=None, redshift=0.0, wave=None, name=None, min_wave=0, max_wave=10000, bottom=0.0, top=1.0, offset=None, style='emission'):
    
    if wave is None:
        linelib = get_linelib()
        wave = linelib['peak'][linelib['primary']>=0]    
        name = linelib['name'][linelib['primary']>=0]    
    if offset is None: 
        offset = [0]*len(wave)
    else:
        offset = [offset]*len(wave)
    line_style = {'emission': '--', 'absorption':':'}
    line_color = {'emission': 'b', 'absorption':'r'}
    position = {'emission': top, 'absorption': bottom}
    alignment = {'emission': 'top', 'absorption': 'bottom'}

    if ax!=None:
        my_axis = ax
    else:
        my_axis = plt

    texts = []
    lines = []

    for lambda_, element, off in zip(wave, name, offset):
        x_pos = lambda_*(1 + redshift)
#        if lambda_*(1 + redshift) > min_wave and lambda_*(1 + redshift) < max_wave :
        t = my_axis.text(x_pos, 
                        position[style]+off, 
                        element, 
                        rotation='vertical', 
                        horizontalalignment='center',
                        verticalalignment=alignment[style], 
                        color=line_color[style], 
                        backgroundcolor='white',
                        fontsize=11)   
        t.set_bbox(dict(alpha=0.05))
        if x_pos < min_wave or x_pos > max_wave:
            t.set_visible(False)
        else:
            t.set_visible(True)
        texts.append(t)

        l = my_axis.axvline(x_pos, 
                        color=line_color[style], 
                        linestyle=line_style[style], 
                        linewidth=0.5, 
                        marker='',
                        zorder=1, alpha=0.5)

        lines.append(l)
    return lines, texts

def air_from_vacuum_wave(vac):
    '''
    http://classic.sdss.org/dr7/products/spectra/vacwavelength.html
    The IAU standard for conversion from air to vacuum wavelengths is given in Morton (1991, ApJS, 77, 119). 
    For vacuum wavelengths (VAC) in Angstroms, convert to air wavelength (AIR) via:
    AIR = VAC / (1.0 + 2.735182E-4 + 131.4182 / VAC^2 + 2.76249E8 / VAC^4)
    '''
    air = vac / (1.0 + 2.735182e-4 + 131.4182 / vac**2. + 2.76249e8 / vac**4.)
    return air

def vacuum_from_air_wave(air):
    '''
    http://classic.sdss.org/dr7/products/spectra/phist.html
    Pat Hall's IRAF tools for SDSS spectra.
    '''
    import numpy as np
    sigma2 = (10**8.)/air**2.
    n = 1 + 0.000064328 + 0.0294981/(146.-sigma2) + 0.0002554/(41.-sigma2)
    vacuum = air * n
    if air<1600:
        raise Warning("Formula intended for use only at >1600 Ang!")    
    return vacuum

