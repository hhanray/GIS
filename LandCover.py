import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

#Define user variables 
f_path = "C:/Users/student/Documents/Ray/Geodatabases/LandCover/Test/"

pathLC = "C:/Users/student/Documents/Ray/Data/Land Cover/Land Cover Data/LC_MCD12Q1_2001.tif"
pathAU = f_path+"/results/assessment_units.shp"
resTable = "standalone_LandCover.dbf"

classifications = ["Forests", "Shrub", "Grass", "PermWet", "Crop", "Urban", "Barren"]
id_field = "Global_ID"

#Create results table and populate with AU fields
arcpy.conversion.TableToTable(pathAU, f_path, resTable)

toDelete = [f.name for f in arcpy.ListFields(f_path+resTable)]
toDelete.remove(id_field)
toDelete.remove("OID")
arcpy.management.DeleteField(f_path+resTable, toDelete)

arcpy.management.CreateFolder(f_path, "lc_temp")

#Process AU by iteratively creating raster of cells corresponding to each land cover classification
for i, type in enumerate(classifications):
    value = str(i+1)
    
    fileLoc = f_path+"lc_temp/LC_MCD12Q1_" + type + ".tif"
    tableLoc = f_path+"lc_temp/Table_" + type
    coverageField = type+"Cover"

    expressionCon = "VALUE=" + value
    expressionCoverage = "!SUM!/!COUNT!"

    out = Con(pathLC,1,0,expressionCon)

    table = ZonalStatisticsAsTable(pathAU, id_field, out, tableLoc, "DATA", "SUM")

    arcpy.AddField_management(tableLoc, coverageField, "DOUBLE")

    arcpy.management.CalculateField(tableLoc, coverageField, expressionCoverage, "PYTHON")

    arcpy.management.JoinField(f_path+resTable, id_field, tableLoc, id_field, coverageField)



arcpy.conversion.TableToTable(f_path+resTable, f_path, "standalone_LandCover.csv")

#Cleanup workspace 
arcpy.management.Delete(f_path+resTable)
arcpy.management.Delete(f_path+"lc_temp")

arcpy.CheckInExtension("Spatial")
