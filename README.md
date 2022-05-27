# Record_linking
Python code to link records and fuzzy match datasets

## Notes
* Fuzzymatcher library can throw errors such as "no such module: fts4" (Windows 11)
  * Solution is to download SQL Lite and copy the binaries to your Python DLL folder
  * If you are using a conda environment this will be similar to: C:\Users\<username>\anaconda3\envs\<conda environment name>\DLLs
  * Reference: https://stackoverflow.com/questions/64155757/error-no-such-module-fts4-using-fuzzymatcher-package-with-anaconda-jupyter
* RecordLinkageToolkit
  * Reference: https://recordlinkage.readthedocs.io/en/latest/index.html
