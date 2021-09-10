# PURPOSE  : chapter1_UpdateFields.py updates fields of feature classes to correct convention.
# INPUTS   : Geodatabase of StreamLinks and/or Assessment Units
#            Completed StreamLinks Geodatabase
# OUTPUTS  : List of basins by grid code missing from StreamLinks
# LAST EDIT: 19 February 2021 by Ray 

import arcpy
from arcpy import env
from arcpy.sa import *

# Features must have the grid code of their basin of origin in their name

# Parameters:
# Change wkDir to point to StreamLinks.gdb
wkDir = "C:/Users/student/Documents/Ray/Geodatabases/Test_GDB/"
wkGDB = "StreamLinks.gdb/"

missing=[]

# Start of Processing 
env.workspace = wkDir + wkGDB
env.overwriteOutput=True
update = arcpy.ListFeatureClasses("*")

unrecognized=[]

print('{} streamlinks and subwatersheds will be updated'.format(len(update)))

for basin in update:
    try:
        # Add indexing
        name = arcpy.Describe(basin).baseName
        code = filter(str.isdigit, str(name))
                
        arcpy.management.AddField(basin, 'basin_id', "LONG")

        with arcpy.da.UpdateCursor(basin, 'basin_id') as cursor:
            for row in cursor:
                row[0]=int(code)
                cursor.updateRow(row)
                
        # Check for type, then add extra indexing for each 
        if name.startswith('StreamLink'):
            arcpy.AlterField_management(basin, 'grid_code', 'au_id')
            arcpy.AlterField_management(basin, 'arcid', 'arc_id')
        elif name.startswith('Subwatershed'):
            arcpy.AlterField_management(basin, 'gridcode', 'au_id')
        else:
            unrecognized.append(name)

        arcpy.Rename_management(basin,  basin+'_QA')

    # Catch and print error messages 
    except arcpy.ExecuteError:
        print (arcpy.GetMessages(2))
        print('Error in Basin {}'.format(basin))
        unrecognized.append(basin)
        continue
    
print('{} streamlinks or subwatersheds were not recognized:'.format(len(unrecognized)))
print(unrecognized)
