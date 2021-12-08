import ee
import math
import numpy as np
import rasterio as rio
from rasterio.warp import transform_bounds

ee.Initialize()


# detect changes in SAR images using Cantys' method
def CalculateCantyDifference(start_date, end_date, file_path, file_name, poly, orbit='ASCENDING',
                             export=False,
                             sum_values=True):
    from SARTools.canty.eeWishart import omnibus

    coords = ee.List(poly.bounds().coordinates().get(0))
    # bounds = ee.Geometry(coords)
    collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(poly) \
        .filterDate(ee.Date(start_date), ee.Date(end_date)) \
        .filter(ee.Filter.eq('transmitterReceiverPolarisation', ['VV', 'VH'])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.eq('orbitProperties_pass', orbit))

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


def CalculateCantyGAUL(point, start_date, end_date, file_path, file_name, orbit='DESCENDING', areaM2=1e6):
    from canty.eeWishart import omnibus

    # convert the point to a square
    poly = ee.Geometry.Point(point).buffer(ee.Number(areaM2).sqrt().divide(2), 1).bounds()

    collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(poly) \
        .filterDate(ee.Date(start_date), ee.Date(end_date)) \
        .filter(ee.Filter.eq('transmitterReceiverPolarisation', ['VV', 'VH'])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.eq('orbitProperties_pass', orbit))

    pcollection = collection.map(get_vvvh)
    pList = pcollection.toList(100)
    first = ee.Dictionary({'imlist': ee.List([]), 'poly': poly, 'enl': ee.Number(4.4)})
    imList = ee.Dictionary(pList.iterate(clipList, first)).get('imlist')

    # make omnibus test for change detection
    result = ee.Dictionary(omnibus(imList, useQ=True))

    result = ee.Image(result.get('cmap')).byte().clip(poly)

    gdexport = ee.batch.Export.image.toDrive(
        result,
        description=file_name,
        folder=file_path,
        maxPixels=1540907088,
        scale=10,
        region=poly
    )
    gdexport.start()


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


def getSARdataFromPoint(point, dates, file_path, file_name, areaM2=1e6, orbit='DESCENDING'):
    from datetime import datetime
    import ee

    ee.Initialize()

    region = ee.Geometry.Point(point).buffer(ee.Number(areaM2).sqrt().divide(2), 1).bounds()

    image = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(region) \
        .filterDate(ee.Date(dates[0]), ee.Date(dates[1])) \
        .filter(ee.Filter.eq('transmitterReceiverPolarisation', ['VV', 'VH'])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .filter(ee.Filter.eq('instrumentMode', 'IW')) \
        .filter(ee.Filter.eq('orbitProperties_pass', orbit)) \
        .mean() \
        .clip(region).float()

    gdexport = ee.batch.Export.image.toDrive(
        image,
        description=file_name,
        folder=file_path,
        maxPixels=1540907088,
        scale=10,
        region=region
    )
    gdexport.start()


def getSARdataFromGAUL(ADM1_NAME, dates, file_path, file_name, dataset):
    from datetime import datetime
    import ee

    ee.Initialize()

    region = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(
        ee.Filter.eq('ADM1_NAME', ADM1_NAME)).first().geometry()

    image = ee.ImageCollection(dataset) \
        .filterBounds(region) \
        .filterDate(ee.Date(dates[0]), ee.Date(dates[1])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .mean() \
        .clip(region).float()

    gdexport = ee.batch.Export.image.toDrive(
        image,
        description=file_name,
        folder=file_path,
        maxPixels=1540907088,
        scale=10,
        region=region
    )
    gdexport.start()


def getSARdata(poly, dates, file_path, file_name):
    from datetime import datetime
    import ee

    ee.Initialize()

    region = ee.Geometry.Polygon(poly)

    image = ee.ImageCollection('COPERNICUS/S1_GRD') \
        .filterBounds(region) \
        .filterDate(ee.Date(dates[0]), ee.Date(dates[1])) \
        .filter(ee.Filter.eq('resolution_meters', 10)) \
        .mean() \
        .clip(region).float()

    gdexport = ee.batch.Export.image.toDrive(
        image,
        description=file_name,
        folder=file_path,
        maxPixels=1540907088,
        scale=10,
        region=region
    )
    gdexport.start()


def pairwise(iterable):
    it = iter(iterable)
    a = next(it, None)

    for b in it:
        yield (a, b)
        a = b


def readGeoTiffasRGB(path):
    # open the georaster and extract it's bands
    with rio.open(path) as geoimage:
        bounds = transform_bounds(geoimage.crs, "epsg:4326", *geoimage.bounds)
        r = geoimage.read(1)
        g = geoimage.read(2)
        b = geoimage.read(3)
    # convert the geo raster to numpy and plot
    image = np.dstack((r, g, b))
    return image, bounds


def readGeoTiffsentinel2(path):
    # open the georaster and extract it's bands
    with rio.open(path) as geoimage:
        b = geoimage.read(1)
        g = geoimage.read(2)
        r = geoimage.read(3)
        re1 = geoimage.read(4)
        re2 = geoimage.read(5)
        re3 = geoimage.read(6)
        nir = geoimage.read(7)
        re4 = geoimage.read(8)
        swir1 = geoimage.read(9)
        swir2 = geoimage.read(10)
        # convert the geo raster to numpy and plot
    image = np.dstack((b, g, r, re1, re2, re3, nir, re4, swir1, swir2))
    return image


def window(seq, n=2):
    from itertools import islice
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def cm_to_inch(value):
    return value / 2.54
