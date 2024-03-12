var assetS2N = 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4'
var imagesS2 = ee.ImageCollection(assetS2N)

print("mosaicos no repositorio Nextgenmap ",imagesS2.aggregate_histogram('year'))

var assetS2W = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4';
var imagesS2W = ee.ImageCollection(assetS2W)

print("mosaicos no repositorio WorkSpace ", imagesS2W.aggregate_histogram('year'))