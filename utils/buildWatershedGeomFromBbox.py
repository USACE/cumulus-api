import math

# Keep floating point for proper division
xmin = 338625.0
ymin = 1228129.0
xmax = 514973.0
ymax = 1521815.0

print('\nOriginal Extents:')
print('xmin: {} \nymin: {} \nxmax: {} \nymax: {}\n'.format(xmin, ymin, xmax, ymax))

buffer = 4000.0 #km
xmin = int((math.floor(xmin/2000)*2000)-buffer)
ymin = int((math.floor(ymin/2000)*2000)-buffer)
xmax = int((math.ceil(xmax/2000)*2000)+buffer)
ymax = int((math.ceil(ymax/2000)*2000)+buffer)

print('\nBuffered Extents:')
print('xmin: {} \nymin: {} \nxmax: {} \nymax: {}\n'.format(xmin, ymin, xmax, ymax))

#-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
output = "ST_GeomFromText('POLYGON (({} {}, {} {}, {} {}, {} {}, {} {}))', 5070)\n".format(xmin, ymax, xmax, ymax, xmax, ymin, xmin, ymin, xmin, ymax)
print(output)