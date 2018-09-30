"""
This script copies the UTRANS road database into a new layer, adds a floating
point 'ANGLE' field, and places the average azimuthal direction of the polyline
in that field.  This is calculated by using the start and end points of the
polyline and ensuring it is a positive number from 0-360 (0 = North, 90 = East,
180 = South, 270 = West).

The new angle field can then be used with SQL statements to identify/select
features where the 'ANGLE' of the road and it's PREDIR or QUADRANTs conflict.
The geometry of these roads would likely need to be flipped or their PREDIR
corrected.

Written by Erik Neemann
"""

from os import path
import arcpy
import time
import math

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "The script start time is {}".format(readable_start)

DB_path = 'C:\Users\eneemann\Desktop\Erik Desktop\UTRANS\Temp_UTRANS.gdb'
Folder_path = 'C:\Users\eneemann\Desktop\Erik Desktop\UTRANS'

# Use test features and create path to it
test_fc = "UTRANS_Roads_Edits_import_180606"
fc_to_edit = path.join(DB_path, test_fc)

# Create FC that is copy of input FC for use later to add fields
temp_layer = 'UTRANS_Roads_Edits_PREDIR_test'
temp_fc = path.join(DB_path, temp_layer)
arcpy.CopyFeatures_management(fc_to_edit, temp_fc)

# Add field to FC that will store primary direction as an angle between 0 and 360
print "adding PREDIR_ANG field to FC..."
arcpy.AddField_management(temp_fc, "ANGLE", "FLOAT")

print "editing ... {}".format(temp_fc)

# Create updateCursor and fields to read/edit; use query to filter, if desired
fields = ['FULLNAME', 'PREDIR', 'QUADRANT_L', 'QUADRANT_R', 'OBJECTID', 'SHAPE@', 'ANGLE']

# Loop through rows & create temporary variables
with arcpy.da.UpdateCursor(temp_fc, fields) as cursor:
    print "Looping through rows in FC ..."
    for row in cursor:
        # print row[0]
        # print row[1]
        # print "Assigning local variables ..."
        name = row[0]
        predir = row[1]
        quadrant_l = row[2]
        quadrant_r = row[3]
        objectid = row[4]
        startx = row[5].firstPoint.X
        starty = row[5].firstPoint.Y
        endx = row[5].lastPoint.X
        endy = row[5].lastPoint.Y

        # calculate mean direction of road in degrees)
        # print "Calculating direction of {} ...".format(name)
        angle = math.degrees(math.atan2((endx - startx), (endy - starty)))
        if angle < 0:
            angle += 360.0
        row[6] = angle

        cursor.updateRow(row)

print "Script shutting down ..."
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print "The script end time is {}".format(readable_end)
print "time elapsed: {:.2f}s".format(time.time() - start_time)
