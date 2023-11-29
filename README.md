# Aibafu App

## Tutorial
1. Modify ```.env``` to config **API_KEY** and **GROUP_ID**.
2. Open ```aibafu_app.exe```.
3. Click ```Choose File``` and select excel file with column ```Link```.
4. The generated file will write to ```{file_name}_shorten.xlsx``` with column ```shorten link```.
5. If the group id in ```.env``` is 0, the shorten link will be generated by today's date as group name.

## Build
```bash
.\build.bat
```

## Version
- V00.00.01:
  1. initial version.
- V00.00.02:
  1. improve log information.
- V00.00.03:
  1. remove 'http://' and 'https://' from link.
- V00.00.04:
  1. prevent covering existing filet.
- V00.00.05: 
  1. resolve the post request error by using json body.
  2. add timeout for shorten link.
- V00.00.06:
  1. use concat every time to prevent the output length dose not match the input length.
  2. add error handling for shorten link.
  3. process the shorten link every 50 links.
- V00.00.07:
  1. create group if the group id in .env is set as 0.
  2. resolve the issue that the last 50 links will not be written to excel.
