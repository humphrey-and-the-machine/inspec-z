class Spectrum():
    def __init__(self):
        self.id_ = ""
        self.ra = ""
        self.dec = ""
        self.z = 0
        self.z_flag = 0
        self.survey = ""
        self.public = 0
        self.calibrated = 0
        self.sp1d_wave = []
        self.sp1d_flux = []
        self.sp1d_error = []
        self.sp1d_mask = []
        self.provenance = ""
        self.origin_catalog_name = ""
        self.origin_1d_name = ""
        self.reference = ""
        self.zphot = 0
        self.zphot_reference = ""
        self.flag = 0
        self.verified = 0
        self.siblings = []
        self.primary = 0
        self.use = 0
        self.z_temp = self.z
        self.flag_temp = self.flag
        self.verified_temp = self.verified
        self.my_flags_dict = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5':5}
        self.flag_broad_dict = {'N':0, 'Y': 1}
        self.verified_dict = {'N':0, 'Y': 1}

        return

    def set_1d(self, wave, flux):
        self.sp1d_wave = wave
        self.sp1d_flux = flux

    def get_1d(self):
        return self.sp1d_wave, self.sp1d_flux
    
    def get_1drestframe(self):
        """
        Get rest frame 1d spectrum. 
        If x- axis is wavelength set wave=True, if energy set wave=False.
        
        Returns:
            x: rest frame wavelength
            y: rest frame flux
        """
        from spectral_analysis import rest_frame
        return rest_frame(self.sp1d_wave, self.sp1d_flux, self.z, wave=True)

    def get_z(self):
        return self.z

    def get_flag(self):
        return self.flag

    def set_flag(self, flag):
        self.flag = int(flag)
        pass

    def set_primary(self, p):
        self.primary = p
        pass
    
    def is_primary(self):
        return self.primary

    def set_siblings(self, s):
        self.siblings = s
        pass

    def get_siblings(self):
        return self.siblings

    def set_use(self, u):
        self.use = u
        pass

    def set_calibration(self, const):
        self.sp1d_wave = self.sp1d_wave * const
        self.calibrated = 1
        pass

    def set_verified(self,v):
        self.verified = v
        pass

    def _set_flag(self, f):
        self.flag_temp = self.my_flags_dict[f]
        pass
    
    def _set_verified(self, v):
        self.verified_temp = self.verified_dict[v]
        pass
    
    




