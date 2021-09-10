# PURPOSE  : chapter1QA.py checks input features to source features to identify duplicated, missing and extra features.
# INPUTS   : StreamLinks or Assessment Units Geodatabase
#            Source Basin shapefile 
# OUTPUTS  : List of basins by grid code that are either duplicated, missing, or incorrectly processed
# LAST EDIT: 25 March 2021 by Ray 

import arcpy
import collections
from arcpy import env
from arcpy.sa import *

# Parameters:
# Change wkDir to point to StreamLinks or Assessment Units Geodatabase, and basins to boundary file
wkDir = "C:/Users/student/Documents/Ray/Geodatabases/Exports/"
wkGDB = "SL_Chapter1.gdb/"
basins = wkDir + "Boundaries_Mar24.shp"

watershedName = "T*"
fields = ['gridcode']
original_gc=[]

# Start of processing 
env.workspace = wkDir + wkGDB
env.overwriteOutput=True
completed = arcpy.ListFeatureClasses(watershedName)

completed_gc = [filter(str.isdigit, str(name)) for name in completed]

with arcpy.da.SearchCursor(basins, fields) as cursor:
    for row in cursor:
        original_gc.append(str(row[0]))

completed_gc.sort()
original_gc.sort()

# Check for duplicated Basins 
print('{} completed basins and {} original basins'.format(len(completed), len(original_gc)))

print('Checking for duplicates...')

duplicates_comp=[basin for basin, count in collections.Counter(completed_gc).items() if count > 1]

duplicates_orig=[basin for basin, count in collections.Counter(original_gc).items() if count > 1]

print('{} basins were duplicated in completed:'.format(len(duplicates_comp)))
print(duplicates_comp)
print('{} basins were duplicated in original:'.format(len(duplicates_orig)))
print(duplicates_orig)


# Check for missing and extra incorrectly processed basins 
print('Checking for missing and extra...')

set_completed=set(completed_gc)
set_original=set(original_gc)

missing=list(sorted(set_original - set_completed))
extra=list(sorted(set_completed - set_original))

# Print all missing and extra basins 
print('{} basins are missing:'.format(len(missing)))
print(missing)

print('{} basins were added:'.format(len(extra)))
print(extra)


