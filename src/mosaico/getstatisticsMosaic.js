var vis = {
    mosaic_Median_Wet: {
        min:10, 
        max: 2500,
        bands: ["red_median_wet","green_median_wet","blue_median_wet"]
    },
    mosaic_Median_Dry: {
        min:10, 
        max: 2500,
        bands: ["red_median_dry","green_median_dry","blue_median_dry"]
    },
};
var lst_bnd = [
        "blue_median_wet","green_median_wet","red_median_wet",
        "nir_median_wet","swir1_median_wet","swir2_median_wet",
        "blue_median_dry","green_median_dry","red_median_dry",
        "nir_median_dry","swir1_median_dry","swir2_median_dry" 
    ];
var get_stats_mean = function(img, geomet){
    // Add reducer output to the Features in the collection.
    var pmtoRed = {
        reducer: ee.Reducer.mean(),
        geometry: geomet,
        scale: 30,
        maxPixels: 1e9
    }
    var statMean = img.reduceRegion(pmtoRed);
    print('viewer stats ', statMean)
    
}
var get_stats_standardDeviations = function(img, geomet){
    // Add reducer output to the Features in the collection.
    var pmtoRed = {
        reducer: ee.Reducer.stdDev(),
        geometry: geomet,
        scale: 30,
        maxPixels: 1e9
    }
    var statstdDev = img.reduceRegion(pmtoRed);
    print('viewer stats Desvio padrão ', statstdDev)
}

var params = {
    'asset_geodatin_work': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4',
    'asset_geodatin_next': 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4',
    'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
    'carta_selected': "SC-24-V-D",
    'subgrade': 0
};
var yearShow = 2020;  

var regiaoCaat = ee.FeatureCollection(params.subGridsAsset)
                        .filter(ee.Filter.eq("grid", params.carta_selected))
                        .filter(ee.Filter.eq("subgrid_id", params.subgrade))
                        .geometry();
var imgColGeodatin = ee.ImageCollection(params.asset_geodatin_next).merge(
                            ee.ImageCollection(params.asset_geodatin_work))
                                .filter(ee.Filter.eq('year', yearShow))
                                .filterBounds(regiaoCaat);

print(" viewer collections ", imgColGeodatin.size());
print("show the first ", imgColGeodatin.first());

var lst_ids = imgColGeodatin.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()

lst_ids.forEach(function(idim){
    print('processin image ' + idim);
    var imgtmp = imgColGeodatin.filter(ee.Filter.eq('system:index', idim)).first();
    var mgeomet = imgtmp.geometry();
    get_stats_mean(imgtmp, mgeomet);
    get_stats_standardDeviations(imgtmp, mgeomet);
})
Map.addLayer(regiaoCaat, {color: 'green'}, 'Grade Caatinga');
Map.addLayer(imgColGeodatin, vis.mosaic_Median_Dry, 'mosaic_Dry_' + yearShow.toString());
Map.addLayer(imgColGeodatin, vis.mosaic_Median_Wet, 'mosaic_Wet_' + yearShow.toString());