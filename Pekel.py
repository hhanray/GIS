import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

#Define threshold and file locations 
threshold = 95

f_path = "C:/Users/student/Documents/Ray/Geodatabases/LandCover/Test/"

tif_path = "C:/Users/student/Documents/Ray/Data/Land Cover/Occurence_Pekel.tif"
pathAU = f_path + "/results/assessment_units.shp"
resTable = "standalone_Pekel.dbf"
id_field = "Global_ID"

#Create results table and populate with AU fields
arcpy.conversion.TableToTable(pathAU, f_path, resTable)

toDelete = [f.name for f in arcpy.ListFields(f_path+resTable)]
toDelete.remove(id_field)
toDelete.remove("OID")
arcpy.management.DeleteField(f_path+resTable, toDelete)

#Create temporary outputs fodler, and define input variabels 
arcpy.management.CreateFolder(f_path, "pkl_temp")

fileLoc = f_path + "pkl_temp/Pekel.tif"
tableLoc = f_path + "pkl_temp/Table_Pekel"
coverageField = "PekelCover"

expressionCon = "VALUE<=100 AND VALUE>="+str(threshold)
expressionCoverage = "!SUM!/!COUNT!"

#Proecss AU for Pekel by creating temporary raster of cells above threshold
out = Con(tif_path,1,0,expressionCon)

table = ZonalStatisticsAsTable(pathAU, id_field, out, tableLoc, "DATA", "SUM")

arcpy.AddField_management(tableLoc, coverageField, "DOUBLE")

arcpy.management.CalculateField(tableLoc, coverageField, expressionCoverage, "PYTHON")

arcpy.management.JoinField(f_path+resTable, id_field, tableLoc, id_field, coverageField)


arcpy.conversion.TableToTable(f_path+resTable, f_path, "standalone_Pekel.csv")

#Clean up workspace 
arcpy.management.Delete(f_path+resTable)
arcpy.management.Delete(f_path+"pkl_temp")

arcpy.CheckInExtension("Spatial")
