# PURPOSE  : chapter1_Delineate.py delineates assessment units within watersheds draining to each uniquely-numbered stream.
# INPUTS   : UpstreamArea raster 
#            Flow Direction raster
#            Geodatabase of basins to process
# OUTPUTS  : Stream.tif
#            StreamLink.tif
#            StreamLink.shp 
#            Watershed.tif
#            Watershed.shp 
# LAST EDIT: 25 March 2021 by Ray 

import sys
import time
import arcpy
from arcpy import env
from arcpy.sa import *

# Export basins to be processed from source shape file to new separate shp,
# then use Split by Attributes Tool to separate into feature classes in gdb
# Feature Naming Convention: 'T[gridcode]'


# Parameters: 
wkDir = "C:/Users/student/Documents/Ray/Geodatabases/Test_GDB/"
wkGDB = "AssessmentUnits.gdb/"
watershedName = "T*"
completed=[]
flagged=[]

# START OF PROCESSING
start=time.time()
env.workspace = wkDir + wkGDB
env.overwriteOutput=True
watersheds = arcpy.ListFeatureClasses(watershedName)

print('The following {} basins will be analyzed:'.format(len(watersheds)))
print(watersheds)

for watershed in watersheds:
    name=arcpy.Describe(watershed).baseName
    
    print("Processing basin: {}".format(watershed))
    arcpy.env.mask = watershed

    #PART 1 ANALYSIS
    try:
        # RASTER CALCULATOR: Extract cells with value over 80 km2 in the UpstreamArea raster.
        UpstreamArea = "UpstreamArea"        
        outStream = (Raster(UpstreamArea) > 70)
        outStream.save( wkDir + wkGDB + "Stream_" + name)

        # STREAM LINK: Assigns unique values to sections of a stream.
        outStreamLink = StreamLink(outStream, "CanFlowDir")
        outStreamLink.save(wkDir + wkGDB + "StreamLinkRas_" + name)

    	#FREQUENCY: Creates a new table containing unique field values and the number of occurrences of each unique field value.        
        arcpy.Frequency_analysis(outStreamLink, wkDir + wkGDB + "Frequency_" + name, "Value", "")

        print("... Part 1 successfully completed")

    except arcpy.ExecuteError:
        print (arcpy.GetMessages(2))
        print('Error in Basin {}'.format(watershed))
        flagged.append(watershed)
        continue

    except:
        print('There has been a non-tool rrror in Basin {}'.format(watershed))
        flagged.append(watershed)
        continue
    
    #FREQUENCY TABLE ANALYSIS

    freqTable = "Frequency_" + name

    with arcpy.da.SearchCursor(freqTable, 'FREQUENCY') as cursor:        
        for row in cursor:
            if row[0]!=1:
                totalrt=time.time()-start
                print("Unexpected values have been observed in {}.".format(name))
                flagged.append(watershed)                
                continue
        print("... Frequency table successfully verified")
        
    #PART 2 ANALYSIS    
    try:        
        outStreamLink = wkDir + wkGDB + "StreamLinkRas_" + name
        # RECLASSIFY: Change the stream link values to range continuously from 1 to total number of stream links.

        outTable = arcpy.BuildRasterAttributeTable_management(outStreamLink, "Overwrite")

        field ="Value"
        oldVal = []
        with arcpy.da.UpdateCursor(outTable, field) as cursor:
            for row in cursor:
                oldVal.append(row[0])

        stop = len(oldVal)
        newVal = list(range(1,stop+1))
        
        remap =[]

        for i,x in zip(range(len(oldVal)),range(len(newVal))):
            inList = []
            inList.append(oldVal[i])
            inList.append(newVal[x])
            remap.append(inList)

        outReclass = Reclassify(outTable, "Value", RemapValue(remap))
        outReclass.save(wkDir + wkGDB + "StreamLinkReclass_" + name)

        # WATERSHED: Determine the contributing area above each stream link.
        outSubwatershed = Watershed("CanFlowDir", outStreamLink)
        outSubwatershed.save(wkDir + wkGDB + "Watershed_" + name)

        # RASTER TO POLYGON: Converts Assessment units to polygon features.
        outSubwatershedPolygon = wkDir + wkGDB + "SubwatershedTemp_" + name
        arcpy.RasterToPolygon_conversion(outSubwatershed, outSubwatershedPolygon, "NO_SIMPLIFY","VALUE")

        # DISSOLVE: Aggregates separated features based on gridcode
        arcpy.Dissolve_management(in_features="SubwatershedTemp_" + name, out_feature_class= wkDir + "StreamLinks.gdb/" + "Subwatershed_" + name,
                           dissolve_field="gridcode", statistics_fields="", multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

        # STREAMS TO FEATURE: Converts stream links to polylines
        outStreamLinkLine = wkDir + "StreamLinks.gdb/" + "StreamLink_" + name
        StreamToFeature(outStreamLink, "CanFlowDir", outStreamLinkLine, "NO_SIMPLIFY")
        
    	# DELETE: Deletes intermediate files. Duplicate code lines were included to ensure certain stubborn files are deleted
        arcpy.management.Delete(r"Stream_" + name)
        arcpy.management.Delete(r"StreamLinkRas_"+ name)        
        arcpy.management.Delete(r"StreamLinkReclass_" + name)
        arcpy.management.Delete(r"Watershed_" + name)
        arcpy.management.Delete(r"SubwatershedTemp_" + name)
        arcpy.management.Delete(r"Frequency_" + name)

        completed.append(watershed)
        print("... Part 2 successfully completed")             

    #Catch errors and return faulty basins    
    except arcpy.ExecuteError:
        print (arcpy.GetMessages(2))
        print('Error in Basin {}'.format(watershed))
        flagged.append(watershed)
        continue

    except:
        print('There has been a non-tool rrror in Basin {}'.format(watershed))
        flagged.append(watershed)
        continue
    
#Print list of succesfully processed basins 
totalrt=time.time()-start
print('Assessment unit generation completed, total runtime: {} seconds. {} basins were analyzed:'.format(totalrt, len(completed)))
print(completed)
print('The following {} watersheds were flagged:'.format(len(flagged)))
print(flagged)
