import ee
import math
import numpy as np

ee.Initialize()


# Calculate monthly changes between two months
def calculate_monthly_changes(start_date, middle_date, final_date, poly, orbit, file_path, export=False):
    print('start: ' + start_date)
    print('middle: ' + middle_date)
    print('final: ' + final_date)

    collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filter(ee.Filter.eq('transmitterReceiverPolarisation', ['VV', 'VH'])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.eq('orbitProperties_pass', orbit)) \
        .filterBounds(poly)

    print(collection.size().getInfo())

    first_month = collection.filterDate(ee.Date(start_date), ee.Date(middle_date)).mean().clip(poly)
    second_month = collection.filterDate(ee.Date(start_date), ee.Date(middle_date)).mean().clip(poly)

    if export:
        gdexport = ee.batch.Export.image.toDrive(
            first_month.toFloat(),
            description='first_month_' + start_date + '_' + middle_date,
            folder=file_path,
            maxPixels=1540907088,
            scale=10,
            region=poly
        )
        gdexport.start()

    collectionFromImages = ee.ImageCollection.fromImages([first_month, second_month])


# detect changes in SAR images using Cantys' method
def CalculateCantyDifference(start_date, end_date, poly, file_path, file_name,
                             orbit='ASCENDING',
                             export=False,
                             sum_values=True):
    from canty.eeWishart import omnibus

    coords = ee.List(poly.bounds().coordinates().get(0))
    # bounds = ee.Geometry(coords)
    collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(poly) \
        .filterDate(ee.Date(start_date), ee.Date(end_date)) \
        .filter(ee.Filter.eq('transmitterReceiverPolarisation', ['VV', 'VH'])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.eq('orbitProperties_pass', orbit)) \


    collection = collection.sort('system:time_start')

    size = collection.size().getInfo()
    print('Hay ' + str(size) + ' imagenes en el mes')
    if size < 2:
        return 0

    pcollection = collection.map(get_vvvh)
    pList = pcollection.toList(100)
    first = ee.Dictionary({'imlist': ee.List([]), 'poly': poly, 'enl': ee.Number(4.4)})
    imList = ee.Dictionary(pList.iterate(clipList, first)).get('imlist')

    # make omnibus test for change detection
    result = ee.Dictionary(omnibus(imList, useQ=True))

    result = ee.Image(result.get('cmap')).byte().clip(poly)

    if (sum_values):
        value = result.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=poly,
            scale=10,
            maxPixels=1e9
        )
        # get and return the sum of all pixel values in image
        value = value.getInfo()
        value = int(value['VV'])
    else:
        value = 0

    if export:
        gdexport = ee.batch.Export.image.toDrive(
            result,
            description=file_name,
            folder=file_path,
            maxPixels=1540907088,
            scale=10,
            region=poly
        )
        gdexport.start()
    return value


def clip_ImageCollection(image, poly):
    return image.clip(poly)


def clipList(current, prev):
    ''' clip a list of images '''
    imlist = ee.List(ee.Dictionary(prev).get('imlist'))
    poly = ee.Dictionary(prev).get('poly')
    enl = ee.Number(ee.Dictionary(prev).get('enl'))
    imlist = imlist.add(ee.Image(current).multiply(enl).clip(poly))
    return ee.Dictionary({'imlist': imlist, 'poly': poly, 'enl': enl})


def get_vvvh(image):
    ''' get 'VV' and 'VH' bands from sentinel-1 imageCollection and restore linear signal from db-values '''
    return image.select('VV', 'VH').multiply(ee.Image.constant(math.log(10.0) / 10.0)).exp()


def pairwise(iterable):
    it = iter(iterable)
    a = next(it, None)

    for b in it:
        yield (a, b)
        a = b


def readGeoTiffAsRGB(path):
    # open the georaster and extract it's bands
    with rio.open(path) as geoimage:
        bounds = transform_bounds(geoimage.crs, "epsg:4326", *geoimage.bounds)
        r = geoimage.read(1)
        g = geoimage.read(2)
        b = geoimage.read(3)
    # convert the geo raster to numpy and plot
    image = np.dstack((r, g, b))
    return image, bounds


def cm_to_inch(value):
    return value / 2.54
