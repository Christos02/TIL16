from osgeo import ogr

# Import files
#stations_in  = 'C:/temp/Kristian/geclipte_stations_test.csv'
stations_in  = 'C:/temp/Kristian/geclipte_stations.csv'
postcodes_in = 'C:/temp/Kristian/cbs_pc4_2019_vol_wgs84.gpkg'
resultaat_uit = 'C:/temp/Kristian/stations_met_aangrenzende_postcodes.csv'

# Load postcode gebieden in memory
postcode_gebieden = []
postcode_stations = []

# Openen bestand
driver = ogr.GetDriverByName('GPKG')
postcode_file = driver.Open(postcodes_in, 0)
layer = postcode_file.GetLayer()

# Open stations file
i = 0
stations_file = open(stations_in)

# Zoek postcode station
print('Zoek postcode gebied voor stations')
for station in stations_file :
    
    # Skip first row
    if i > 0 and len(station.split(',')) > 1:
        station_naam = station.split(',')[3]
        y = float(station.split(',')[10])
        x = float(station.split(',')[11])
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)

        # Zoek postcode
        #print('Zoek postcode voor station ' + station_naam)
        for feature in layer:
            postcode_geom = feature.GetGeometryRef()
            intersection = postcode_geom.Intersection(point)
            if intersection.ExportToWkt() != 'POINT EMPTY':
                #print(feature.GetField('postcode4'))
                postcode_station = {}
                postcode_station['station'] = station_naam
                postcode_station['postcode'] = feature.GetField('postcode4')
                postcode_station['postcode_area'] = feature.GetGeometryRef().ExportToWkt()
                postcode_stations.append(postcode_station)

    # next station
    i = i + 1
    if i % 50 == 0 :
        print(str(int(i/2)) + ' stations processed')

# Close file
stations_file.close()

# Open outputfile
resultaat_file = open(resultaat_uit,'w')
header = 'station_naam;postcode_gebied_station;postcode_aangrenzende_postcode_gebieden'
resultaat_file.write(header + '\n')

# Aantal station
print('Aantal stations met postcode ' + str(len(postcode_stations)))

# Zoek aangrenzende postcode gebieden voor postcode gebied stations
print('Zoek aangrenzende postcode gebieden voor postcode gebied stations')
i = 0
for postcode_station in postcode_stations:

    # Haal station attributen op
    station_name = postcode_station['station']
    station_postcode = postcode_station['postcode']
    #print('Zoek postcodes voor station ' + station_name + ' met postcode ' + station_postcode)

    # Definieer output regel
    output_regel = station_name + ';' + station_postcode + ';'

    # Bereken een kleine buffer om postcode gebied station (in decimale graden)
    postcode_polygon_station = ogr.CreateGeometryFromWkt(postcode_station['postcode_area'])
    bufferDistance = 0.000001 
    postcode_polygon_station_buf = postcode_polygon_station.Buffer(bufferDistance)

    # Zoek aangrenzende postcodes
    for feature in layer:
        postcode_geom = feature.GetGeometryRef()
        intersection = postcode_geom.Intersection(postcode_polygon_station_buf)
        if intersection.ExportToWkt() != 'POLYGON EMPTY':
            #print(feature.GetField('postcode4'))
            output_regel = output_regel + feature.GetField('postcode4') + ','

    # Schrijf naar output file
    resultaat_file.write(output_regel[:-1] + '\n')

    # next station
    i = i + 1
    if i % 25 == 0 :
        print(str(i) + ' stations processed')
    
# Close file
resultaat_file.close()
postcode_file = None

# Script klaar
print('Script klaar')
