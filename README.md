# inspec-z
Interactive inspection and validation of 1D spectra.

# Run sequence

1. Edit or create `yaml` configuration file in `config_files` folder
2. Prepare catalog: `python prepare_catalog.py`.
3. Run main program: `python inspecz.py`.
4. Merge results with initial data file and get report: `python finalize.py`.
