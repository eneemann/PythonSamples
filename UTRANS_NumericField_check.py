"""
This script corrects alias name errors in the UTRANS road database, like alpha aliases that should be in the numeric aliases field.  It loops through each feature, reads the alias fields ('A1_NAME' and 'A2_NAME), and moves them into the numeric alias field ('AN_NAME') if it contains only integers and directions (N, S, E, W, North, South, East, West, etc.).

Written by Erik Neemann
"""



from os import path
import arcpy
import time

start_time = time.time()

DB_path = 'Database Connections\\eneemann@utrans.agrc.utah.gov.sde'
FC_layer = 'UTRANS.TRANSADMIN.Centerlines_Edit\\UTRANS.TRANSADMIN.Roads_Edit'

# Path to primary feature class
fc = path.join(DB_path, FC_layer)

# # Use test features and create path
# test_fc = "ggg_UTRANS_Roads_Edits_test"
# fc_to_edit = path.join(DB_path, test_fc)

print DB_path

# Initialize list of roads that are editing and count variable
roadlist = []
update_num = 0

# Open an edit session and start an edit operation
edit = arcpy.da.Editor(DB_path)
edit.startEditing(False, True)
edit.startOperation()

# Create updateCursor and fields to read/edit; use query to filter, if desired
# query = """ADDRSYS_L = 'CEDAR CITY'"""
cursor = arcpy.da.UpdateCursor(fc, ['NAME',
                                    'POSTTYPE',
                                    'POSTDIR',
                                    'A1_NAME',
                                    'A1_POSTTYPE',
                                    'A1_POSTDIR',
                                    'AN_NAME',
                                    'AN_POSTDIR',
                                    'OBJECTID',
                                    'A2_NAME',
                                    'A2_POSTTYPE',
                                    'A2_POSTDIR']) #, query)

# Loop through rows & create temporary dictionary of values
for row in cursor:
    temp_dict = {}
    temp_dict['name'] = row[0]
    temp_dict['posttype'] = row[1]
    temp_dict['postdir'] = row[2]
    temp_dict['a1_name'] = row[3]
    temp_dict['a1_posttype'] = row[4]
    temp_dict['a1_postdir'] = row[5]
    temp_dict['an_name'] = row[6]
    temp_dict['an_postdir'] = row[7]
    temp_dict['objectid'] = row[8]
    temp_dict['a2_name'] = row[9]
    temp_dict['a2_posttype'] = row[10]
    temp_dict['a2_postdir'] = row[11]

# Create variable to hold string that is the split of A1_NAME
    if temp_dict['a1_name'] is not None:
        a1_name_split = temp_dict['a1_name'].split(" ")
        # print "checking OBJECTID: {}".format(temp_dict['objectid'])
        # check for valid numeric in 1st part of A1_NAME and direction in A1_POSTTYPE
        if a1_name_split[0].isdigit() and temp_dict['a1_posttype'] in ('N', 'S', 'E', 'W'):
            # Move a1_name_split[0] to an_name and a1_posttype to an_postdir
            print "editing OBJECTID: {}".format(temp_dict['objectid'])
            row[6] = a1_name_split[0]
            row[7] = temp_dict['a1_posttype']
            # Change to blank: a1_name, a1_posttype, a1_postdir
            row[3] = ''
            row[4] = ''
            row[5] = ''
            update_num += 1
            roadlist.append([temp_dict['objectid'], temp_dict['name']])

        elif len(a1_name_split) == 2 and a1_name_split[0].isdigit() and a1_name_split[1] in ('N', 'S', 'E', 'W', 'NORTH', 'SOUTH', 'EAST', 'WEST'):
            # Move a1_name_split[0] to an_name and a1_name_split[1] an_postdir
            print "editing OBJECTID: {}".format(temp_dict['objectid'])
            row[6] = a1_name_split[0]
            row[7] = a1_name_split[1].title()[0]
            # Change to blank: a1_name, a1_posttype, a1_postdir
            row[3] = ''
            row[4] = ''
            row[5] = ''
            update_num += 1
            roadlist.append([temp_dict['objectid'], temp_dict['name']])

        # check for 3-part A1_NAME w/ 'SB' or 'NB' and direction
        elif (len(a1_name_split) == 3 and a1_name_split[0].isdigit() and
            a1_name_split[1] in ('N', 'S', 'E', 'W', 'NORTH', 'SOUTH', 'EAST', 'WEST') and
            a1_name_split[2] in ('NB', 'SB', 'EB', 'WB')):
            # Move primary and SB/NB to AN_NAME and direction to AN_POSTDIR
            print "editing OBJECTID: {}".format(temp_dict['objectid'])
            new_name = a1_name_split[0] + " " + a1_name_split[2]
            row[6] = new_name
            row[7] = a1_name_split[1].title()[0]
            # Change to blank: a1_name, a1_posttype, a1_postdir
            row[3] = ''
            row[4] = ''
            row[5] = ''
            update_num += 1
            roadlist.append([temp_dict['objectid'], temp_dict['name']])
        # Only apply row update at end of loop
        cursor.updateRow(row)

    if temp_dict['a2_name'] is not None:
        a2_name_split = temp_dict['a2_name'].split(" ")
        # print "checking OBJECTID: {}".format(temp_dict['objectid'])
        # check for valid numeric in 1st part of A2_NAME and direction in A2_POSTTYPE
        if a2_name_split[0].isdigit() and temp_dict['a2_posttype'] in ('N', 'S', 'E', 'W'):
            # Move a2_name_split[0] to an_name and a2_posttype to an_postdir
            print "editing OBJECTID: {}".format(temp_dict['objectid'])
            row[6] = a2_name_split[0]
            row[7] = temp_dict['a2_posttype']
            # Change to blank: a2_name, a2_posttype, a2_postdir
            row[9] = ''
            row[10] = ''
            row[11] = ''
            update_num += 1
            roadlist.append([temp_dict['objectid'], temp_dict['name']])

        # check for valid numeric in 1st part of A2_NAME and direction in A2_POSTTYPE
        elif len(a2_name_split) == 2 and a2_name_split[0].isdigit() and a2_name_split[1] in ('N', 'S', 'E', 'W', 'NORTH', 'SOUTH', 'EAST', 'WEST'):
            # Move a2_name_split[0] to an_name and a2_name_split[1] an_postdir
            print "editing OBJECTID: {}".format(temp_dict['objectid'])
            row[6] = a2_name_split[0]
            row[7] = a2_name_split[1].title()[0]
            # Change to blank: a2_name, a2_posttype, a2_postdir
            row[9] = ''
            row[10] = ''
            row[11] = ''
            update_num += 1
            roadlist.append([temp_dict['objectid'], temp_dict['name']])

        # check for 3-part A2_NAME w/ 'SB' or 'NB' and direction
        elif (len(a2_name_split) == 3 and a2_name_split[0].isdigit() and
            a2_name_split[1] in ('N', 'S', 'E', 'W', 'NORTH', 'SOUTH', 'EAST', 'WEST') and
            a2_name_split[2] in ('NB', 'SB', 'EB', 'WB')):
            # Move primary and SB/NB to AN_NAME and direction to AN_POSTDIR
            print "editing OBJECTID: {}".format(temp_dict['objectid'])
            new_name = a2_name_split[0] + " " + a2_name_split[2]
            row[6] = new_name
            row[7] = a2_name_split[1].title()[0]
            # Change to blank: a2_name, a2_posttype, a2_postdir
            row[9] = ''
            row[10] = ''
            row[11] = ''
            update_num += 1
            roadlist.append([temp_dict['objectid'], temp_dict['name']])
        # Only apply row update at end of loop
        cursor.updateRow(row)

del cursor
del row		
		
edit.stopOperation()
edit.stopEditing(True)

for item in roadlist:
    print item
print len(roadlist)

print "time elapsed: {:.2f}s".format(time.time() - start_time)

