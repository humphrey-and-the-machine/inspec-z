# inspec-z
Interactive inspection and validation of 1D spectra.

# Environment installation
Clone package locally:

```git clone git@github.com:d-i-an-a/inspec-z.git
cd inspec-z
```

Inspec-z requires: `python`, `pyyaml`, `numpy`, `astropy`, `scipy`, `tqdm` and `matplotlib`.

A conda environment is recommended. Either install the latest version of the required packages:

```
conda create --name inspec-z
conda activate inspec-z
conda install python pyyaml numpy astropy matplotlib tqdm scipy
```
or install the lastest tested version:

`conda create --name  inspec-z --file requirements.txt`

# Run sequence
An example configuration and data files are provided.

1. Edit or create the `yaml` configuration file in `config_files` folder.
- Set up the file paths and file names. To follow the example replace `/path/to/` with the path to the folder containing the `inspec-z` code.
- Change the selection of the sample to be inspected.

2. Prepare catalog: `python prepare_catalog.py`.
3. Run main program: `python inspecz.py`.
4. Merge results with initial data file and get report: `python finalize.py`.


