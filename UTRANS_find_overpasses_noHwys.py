"""
This script reads in the UTRANS roads data (a copy from a local geodatabase),
identifies potential overpasses or intersections with unbroken road segments,
and writes them out to a CSV file.  UDOT highways are skipped, along with all
roads with a valid entry in the 'VERT_LEVEL' field.

The remaining rows in the CSV are features that should be examined to add a
VERT_LEVEL.  By fixing the VERT_LEVEL field, the roads data could later be
broken at all intersections without erroneously breaking road segments at
overpasses.

Written by Erik Neemann
"""

from os import path
import arcpy
import time
import datetime

start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "The script start time is {}".format(readable_start)

DB_path = 'C:\Users\eneemann\Desktop\Erik Desktop\UTRANS\Temp_UTRANS.gdb'
Folder_path = 'C:\Users\eneemann\Desktop\Erik Desktop\UTRANS'
FC_layer = 'UTRANS_Roads_Edits_import'
# Path to primary feature class
fc = path.join(DB_path, FC_layer)

# Use test features and create path to it
test_fc = "UTRANS_Roads_Edits_test_180522_try2"
fc_to_edit = path.join(DB_path, test_fc)

print "editing ... {}".format(fc_to_edit)

print "Converting road end points to point feature class..."
# VerticesToPoints: Convert end points of roads to point feature class
inRoads = fc_to_edit
outPts = path.join(DB_path, 'Roads_EndPts')
arcpy.FeatureVerticesToPoints_management(inRoads, outPts, "BOTH_ENDS")

print "Buffering road end points..."
# Buffer: Buffer the road end points by 2m to create small polygons
buffInput = outPts
buffOutput = path.join(DB_path, 'Roads_EndPts_2m_buff')
buffDistance = '2 Meters'
arcpy.Buffer_analysis(buffInput, buffOutput, buffDistance)

print "Shortening road segments by buffer distance..."
# Erase: Shorten road segments by the 2m buffers with erase tool
eraseInput = fc_to_edit
eraseFeature = buffOutput
eraseOutput = path.join(DB_path, 'Roads_Shortened')
arcpy.Erase_analysis(eraseInput, eraseFeature, eraseOutput)

print "Intersecting roads to find overpasses..."
# Intersect: Find where shortened roads intersect to identify overpasses (and unbroken intersections)
intersectInput = [eraseOutput]     # This input must be a list!
# intersectInput = [path.join(DB_path, 'Roads_Shortened')]
intersectOutput = path.join(DB_path, 'Roads_Overpasses')
join_attributes = 'ALL'
cluster_tolerance = 0.05
output_type = 'POINT'
arcpy.Intersect_analysis(intersectInput, intersectOutput, join_attributes, cluster_tolerance, output_type)

intersectOutput = path.join(DB_path, 'Roads_Overpasses')
print "Creating feature layer for selection..."
# Select by Location: Select roads that are associated with overpasses
# First make feature layer to use for selection
arcpy.MakeFeatureLayer_management(fc_to_edit, 'Roads_lyr')

print "Selecting roads associated with overpasses..."
# Then add a selection to the layer based on location to features in another feature class
selectInput = 'Roads_lyr'
overlap_type = 'INTERSECT'
select_features = intersectOutput
search_distance = 1.9
# arcpy.SelectLayerByLocation_management(selectInput, overlap_type, intersectOutput)
arcpy.SelectLayerByLocation_management(selectInput, overlap_type, intersectOutput, search_distance)
select_count = int(arcpy.GetCount_management('Roads_lyr')[0])
print "Selection found {} roads".format(select_count)

# Write Selection out to CSV file (try to reduce to only FULLNAME and UNIQUE_ID fields)
CSVFile = path.join(Folder_path, 'Overpasses_2m_UDOT_noHwys_emptyVert.csv')
print "Writing out selected roads to CSV file: {}".format(CSVFile)
fields = ['FULLNAME', 'UNIQUE_ID', 'VERT_LEVEL', 'DOT_RTNAME']

# Write out certain records to CSV based on attributes
with open(CSVFile, 'w') as f:
    f.write(','.join(fields) + '\n')  # csv headers
    with arcpy.da.SearchCursor(selectInput, fields) as cursor:
        for row in cursor:
            print "item 2 is: {}".format(row[2])
            print "item 3 is: {}".format(row[3])
            if row[3] is not None and 'DOT' in row[3]:                  # Catch headers and print
                print "writing to file..."
                f.write(','.join([str(r) for r in row]) + '\n')
            elif row[3] in (None, '', ' '):                             # Empty in UDOT_Route field
                if row[2] in (None, '', ' '):                           # Empty in VERT_LEVEL field
                    print "writing to file..."
                    f.write(','.join([str(r) for r in row]) + '\n')
                else:                                                   # Empty UDOT field and valid VERT_LEVEL
                    print "skipping..."
            elif int(row[3][0:4]) < 1000:                               # UDOT Highway, skip
                    print "skipping..."
            elif int(row[3][0:4]) >= 1000:                              # UDOT non-highway
                if row[2] in (None, '', ' '):                           # Empty VERT_LEVEL field, print
                    print "writing to file..."
                    f.write(','.join([str(r) for r in row]) + '\n')
                else:                                                   # Valid VERT_LEVEL, skip
                    print "skipping..."
            else:                                                       # All other cases
                print "writing to file..."
                f.write(','.join([str(r) for r in row]) + '\n')

print "Script shutting down..."
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "The script end time is {}".format(readable_end)

print "Time elapsed: {:.2f}s".format(time.time() - start_time)

