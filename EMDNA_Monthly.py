# Resamples nc4 data to monthly averages/totals
# Last updated Dec. 29, 2021 by Ray 

import xarray as xr
import pandas as pd
from os import listdir

# Return the given DatayArray resampled to monthly averages
def monthlyAverage(da, year):    
    month_cnt = (da.time.dt.year.to_index() - year) * 12 + da.time.dt.month.to_index()
    return da.assign_coords(year_month = month_cnt).groupby('year_month').mean()

# Return the given DatayArray resampled to monthly totals
def monthlySum(da, year):    
    month_cnt = (da.time.dt.year.to_index() - year) * 12 + da.time.dt.month.to_index()
    return da.assign_coords(year_month = month_cnt).groupby('year_month').sum()

# Path to directory containing all nc4 data files 
dataPath = "C:/Users/Ray/Documents/School/HGS-WM/EMDNA Project/Data/EMDNA_Raw/"

# Path to save resampled data to 
savePath = "C:/Users/Ray/Documents/School/HGS-WM/EMDNA Project/Data/EMDNA_Monthly/"
allFiles = listdir(dataPath)


print("Resampling: ")
for file in allFiles:
    # Get year from file name 
    year = int(file[3:7])
    print("{}".format(year), end = '...')
    
    # Open file, then modify time dimension to DateTime64 type
    ds = xr.open_dataset(dataPath + file, decode_times = True)
    ds['time'] = pd.DatetimeIndex(pd.to_datetime(ds['date'].values, format = '%Y%m%d'))
    
    # Resample then save variables
    meanPrecip = monthlyAverage(ds.prcp, year)
    totalPrecip = monthlySum(ds.prcp, year)
    temp = monthlyAverage(ds.tmean, year)
    
    meanPrecip.to_netcdf("{savePath}MeanPrecipitation/Monthly_OI_{year}.nc4".format(savePath = savePath,year = year))
    totalPrecip.to_netcdf("{savePath}TotalPrecipitation/Monthly_OI_{year}.nc4".format(savePath = savePath,year = year))
    temp.to_netcdf("{savePath}Temperature/Monthly_OI_{year}.nc4".format(savePath = savePath,year = year))


    
