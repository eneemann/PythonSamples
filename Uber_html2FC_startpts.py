"""
This script was used to populate a feature class of Uber ride starting points.  It loops through HTML files in the specified directory, each file representing one Uber trip.

The code does the following:
1) Creates point feature class in default.gdb to place Uber points
2) Iterates through and reads local HTML files of individual Uber trips in directory
3) Parses HTML for trip attributes and addresses, places them in a dictionary
4) Feeds addresses to Utah AGRC Geocoder for geolocating
5) Populates FC with the starting point for each Uber trip/html file

Written by Erik Neemann
v1: 13 May 2018
"""

import time
start_time = time.time()

from bs4 import BeautifulSoup
import codecs
import os
import arcpy
import geocode as geocode

#################
#   Functions   #
#################

def address_parser(full_address):
    print full_address.split(',')
    # If missing street number, make destination the airport
    if len(full_address.split(',')) < 3:
        if full_address.split(',')[1].split(' ')[2] == '84116' or full_address.split(',')[1].split(' ')[2] == '84122':
            full_address = '776 N Terminal Dr, ' + full_address
        elif full_address.split(',')[1].split(' ')[2] == '84107':
            full_address = '140 W Vine St, ' + full_address

    print full_address

    # Determine if street number is provided as range, if so take endpoint
    if '-' in full_address.split(' ')[0]:
        clean = full_address.split('-', 1)[1]
    else:
        clean = full_address
    # Separate into street, city, zone
    street = clean.split(',')[0].strip()
    city = clean.split(',')[1].strip()
    zone = clean.split(',')[2].strip().split(' ')[1]
    # build dictionary & return
    dictadd = {"street": street,
               "city": city,
               "zone": zone}

    # Strip off unit numbers from "street"
    if '#' in dictadd['street']:
        clean = dictadd['street'].split('#')[0]
    elif ' Apt' in dictadd['street']:
        clean = dictadd['street'].split('Apt')[0]
    elif ' apt' in dictadd['street']:
        clean = dictadd['street'].split('apt')[0]
    elif 'Unit' in dictadd['street']:
        clean = dictadd['street'].split('#')[0]
    elif 'unit' in dictadd['street']:
        clean = dictadd['street'].split('#')[0]
    elif '&' in dictadd['street']:
        clean = dictadd['street'].replace('&', 'and')
    else:
        clean = dictadd['street']

    dictadd['street'] = clean
    print dictadd['street']

    return dictadd

##########################################
#   Step 1: Create point feature class   #
##########################################

# Set local variables
default_dir = "C:\\Users\\Erik\\Documents\\ArcGIS\\Default.gdb"
out_path = default_dir
out_name = "aaa_1_uber_startpts_test"
geometry_type = "POINT"
template = "C:\\Users\\Erik\\Documents\\ArcGIS\\Default.gdb\\uber_pts_template"
has_m = "DISABLED"
has_z = "DISABLED"
spatial_reference = arcpy.SpatialReference(4326)

# create point feature class
print 'Creating feature class...'
arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type, template, has_m, has_z, spatial_reference)


##########################################
#   Step 2: Iterate through HTML files   #
##########################################
directory = "C:\\Users\\Erik\\Desktop\\MSGIS Fall 2017\\6000 - Adv Geog Data Analysis\\Uber Data\\html files\\"
filenumber = 0

for filename in os.listdir(directory):
    filenumber += 1
    print 'Starting on file number: {}'.format(filenumber)
    if filename.endswith(".html"):
        print 'The filename is: {}'.format(filename)
        number = filename.split('_')[1].split('.')[0]
        ride = "trip" + number

##########################################################
#   Step 3: Parse HTML files, populate trip dictionary   #
##########################################################

        # Create trip dictionary
        trip = {'TripID': number}
        trip['Duration'] = None
        trip['Distance'] = None
        trip['EarnTotal'] = None
        trip['FareTotal'] = None
        trip['Tip'] = None
        trip['Surge'] = None
        trip['Type'] = None
        trip['StartAdd'] = None
        trip['EndAdd'] = None
        trip['Gender'] = None
        trip['ReqTime'] = None
        trip['StartTime'] = None
        trip['EndTime'] = None
        trip['Airport'] = None
        trip['Date'] = None
        trip['Lat_Start'] = None
        trip['Lat_End'] = None
        trip['Lon_Start'] = None
        trip['Lon_End'] = None

        path = directory + filename
        page = codecs.open(path,'r','utf-8')
        soup = BeautifulSoup(page, "lxml")

        # Find and extract Distance & Duration info
        liclass = soup.find_all("li", class_="_style_2tQ3lo")

        lidict = {}
        for x in range(len(liclass)):
            lidict['part' + str(x)] = liclass[x].text

        if 'Tip' in lidict['part3']:
            trip['Tip'] = str(lidict['part3'].split('$')[1])
            divclassdist = soup.find_all("div", class_="_style_3HjmOn")
            distdict = {}
            for x in range(len(divclassdist)):
                distdict['part' + str(x)] = divclassdist[x].text
            trip['Distance'] = str(distdict['part1'].split(' ')[0])
            min = distdict['part0'].split('min')[0]
            sec = distdict['part0'].split('sec')[0].split(' ')[1]
            dec = format((float(sec) / 60), '.2f')
            dur = str(min) + dec.split('0', 1)[1]
            trip['Duration'] = dur
        elif 'Tip' in lidict['part4']:
            trip['Tip'] = str(lidict['part4'].split('$')[1])
            divclassdist = soup.find_all("div", class_="_style_3HjmOn")
            distdict = {}
            for x in range(len(divclassdist)):
                distdict['part' + str(x)] = divclassdist[x].text
            trip['Distance'] = str(distdict['part1'].split(' ')[0])
            min = distdict['part0'].split('min')[0]
            sec = distdict['part0'].split('sec')[0].split(' ')[1]
            dec = format((float(sec) / 60), '.2f')
            dur = str(min) + dec.split('0', 1)[1]
            trip['Duration'] = dur
        else:
            divclassdist = soup.find_all("div", class_="_style_3HjmOn")
            distdict = {}
            for x in range(len(divclassdist)):
                distdict['part' + str(x)] = divclassdist[x].text
            trip['Distance'] = str(distdict['part1'].split(' ')[0])
            min = distdict['part0'].split('min')[0]
            sec = distdict['part0'].split('sec')[0].split(' ')[1]
            dec = format((float(sec) / 60), '.2f')
            dur = str(min) + dec.split('0', 1)[1]
            trip['Duration'] = dur


        # Find and extract FareTotal info
        h6class = soup.find_all("h6", class_="_style_3muff1")

        h6dict = {}
        for x in range(len(h6class)):
            h6dict['part' + str(x)] = h6class[x].text
        trip['FareTotal'] = str(h6dict['part3'].split('$')[1])

        # Find and extract StartAdd & EndAdd info
        divclass1 = soup.find_all("div", class_="_style_2AyT2x")

        div1dict = {}
        for x in range(len(divclass1)):
            div1dict['part' + str(x)] = divclass1[x].text
        if 'AM' in div1dict['part0'].split(':')[1]:
            if 'US' in div1dict['part0'].split(':')[1]:
                temp_start = str(div1dict['part0'].split(':')[1].split('AM')[1].split(', US')[0])
            else:
                temp_start = str(div1dict['part0'].split(':')[1].split('AM')[1].split(', Uni')[0])
        elif 'PM' in div1dict['part0'].split(':')[1]:
            if 'US' in div1dict['part0'].split(':')[1]:
                temp_start = str(div1dict['part0'].split(':')[1].split('PM')[1].split(', US')[0])
            else:
                temp_start = str(div1dict['part0'].split(':')[1].split('PM')[1].split(', Uni')[0])
        if '-' in temp_start.split(' ')[0]:
            clean_start = temp_start.split('-', 1)[1]
        else:
            clean_start = temp_start
        trip['StartAdd'] = clean_start

        if 'AM' in div1dict['part0'].split(':')[2]:
            if 'US' in div1dict['part0'].split(':')[2]:
                temp_end = str(div1dict['part0'].split(':')[2].split('AM')[1].split(', US')[0])
            else:
                temp_end = str(div1dict['part0'].split(':')[2].split('AM')[1].split(', Uni')[0])
        elif 'PM' in div1dict['part0'].split(':')[2]:
            if 'US' in div1dict['part0'].split(':')[2]:
                temp_end = str(div1dict['part0'].split(':')[2].split('PM')[1].split(', US')[0])
            else:
                temp_end = str(div1dict['part0'].split(':')[2].split('PM')[1].split(', Uni')[0])
        if '-' in temp_end.split(' ')[0]:
            clean_end = temp_end.split('-', 1)[1]
        else:
            clean_end = temp_end
        trip['EndAdd'] = clean_end

        # Find and extract Trip Type info
        divclass2 = soup.find_all("div", class_="_style_375kRm")

        div2dict = {}
        for x in range(len(divclass2)):
            div2dict['part' + str(x)] = divclass2[x].text
        trip['Type'] = str(div2dict['part1'].split('Vehicle')[1])

        # Find and extract EarnTotal info
        divclass3 = soup.find_all("div", class_="_style_2Ughki")

        div3dict = {}
        for x in range(len(divclass3)):
            div3dict['part' + str(x)] = divclass3[x].text
        trip['EarnTotal'] = str(div3dict['part0'].split('$')[1])

        # Find and extract Surge info
        divclass4 = soup.find_all("div", class_="_style_4pQlm1")

        div4dict = {}
        for x in range(len(divclass4)):
            div4dict['part' + str(x)] = divclass4[x].text

        if 'Surge' in div4dict['part4']:
            trip['Surge'] = str(div4dict['part4'].split('(')[1].split('x')[0])
        elif 'Surge' in div4dict['part5']:
            trip['Surge'] = str(div4dict['part5'].split('(')[1].split('x')[0])
        else:
            pass

        # Catch and remove illegal characters
        if '&' in trip['EndAdd']:
            temp = trip['EndAdd'].replace('&', 'and')
            trip['EndAdd'] = temp
        elif '#' in trip['EndAdd']:
            temp = trip['EndAdd'].replace('#', '')
            trip['EndAdd'] = temp

        if '&' in trip['StartAdd']:
            temp = trip['StartAdd'].replace('&', 'and')
            trip['StartAdd'] = temp
        elif '#' in trip['StartAdd']:
            temp = trip['StartAdd'].replace('#', '')
            trip['StartAdd'] = temp

        # Fix 'EE. UU.' issue for phones in spanish
        if 'EE. UU.' in trip['StartAdd']:
            temp = trip['StartAdd'].replace('EE. UU.', 'US')
            trip['StartAdd'] = temp
        if 'EE. UU.' in trip['EndAdd']:
            temp = trip['EndAdd'].replace('EE. UU.', 'US')
            trip['EndAdd'] = temp

        # Fix 26th E address issue
        if '26th E' in trip['EndAdd']:
            fix = trip['EndAdd'].replace('26th', '2600')
            trip['EndAdd'] = fix
        elif '26th E' in trip['StartAdd']:
            fix = trip['StartAdd'].replace('26th', '2600')
            trip['StartAdd'] = fix

        print trip

        # # check to make sure address is complete with street number
        # if len(trip['StartAdd'].split(',')) > 2 and len(trip['EndAdd'].split(',')) > 2:


##########################################
#   Step 4: Feed addresses to Geocoder   #
##########################################

        # Input addresses
        temp_address = trip['StartAdd']

        # Test on addresses
        add1 = address_parser(temp_address)
        print add1

        # def dict_to_json(dict_add):
        self = 'AGRC-XXXXXXXXXXXXX'     # insert correct API token here
        add1_loc = geocode.Geocoder(self).locate(add1['street'], add1['zone'],
                                                 **{"acceptScore": 80, "spatialReference": 4326})
        print add1_loc

        trip['Lat_End'] = str(add1_loc['y'])
        trip['Lon_End'] = str(add1_loc['x'])

#################################################################
#   Step 5: Populate FC with point from Uber trip/html file   #
#################################################################

        # Create list of fields for the insertCursor
        fields = ['Distance',
                  'Type',
                  'FareTotal',
                  'TripID',
                  'POINT_X',
                  'POINT_Y',
                  'Gender',
                  'EndAdd',
                  'Tip',
                  'Surge',
                  'Duration',
                  'Airport',
                  'StartAdd',
                  'Date',
                  'EarnTotal',
                  'SHAPE@XY']

        xy = (float(trip['Lon_End']), float(trip['Lat_End']))

        # Prep potential null values
        if trip['Tip'] == None:
            tip = None
        else:
            tip = float(trip['Tip'])
        if trip['Surge'] == None:
            surge = None
        else:
            surge = float(trip['Surge'])

        # Shorten addresses that are too long
        if len(trip['EndAdd']) > 50:
            short = trip['EndAdd'].replace('Salt Lake City', 'SLC')
            trip['EndAdd'] = short
        elif len(trip['StartAdd']) > 50:
            short = trip['StartAdd'].replace('Salt Lake City', 'SLC')
            trip['StartAdd'] = short

        values = [float(trip['Distance']),
                  trip['Type'],
                  float(trip['FareTotal']),
                  int(trip['TripID']),
                  float(trip['Lon_End']),
                  float(trip['Lat_End']),
                  trip['Gender'],
                  trip['EndAdd'],
                  tip,
                  surge,
                  float(trip['Duration']),
                  trip['Airport'],
                  trip['StartAdd'],
                  trip['Date'],
                  float(trip['EarnTotal']),
                  xy]

        # add point to FC
        print 'Adding point to feature class...'
        fc = "C:\\Users\\Erik\\Documents\\ArcGIS\\Default.gdb\\aaa_1_uber_startpts_test"
        cursor = arcpy.da.InsertCursor(fc, fields)

        print 'Inserting point...'
        print values
        cursor.insertRow(values)

        del cursor

    else:
        print 'Not an HTML file'

print "time elapsed: {:.2f}s".format(time.time() - start_time)