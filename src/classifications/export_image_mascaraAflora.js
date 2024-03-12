// https://code.earthengine.google.com/0b54da7e9394b492266c405aadb593da
//exporta a imagem classificada para o asset
var processoExportarImage = function (imageMap, nameB, idAssetF, regionB){
    var idasset =  idAssetF + "/" + nameB
    print("saving ")
    var optExp = {
            'image': imageMap, 
            'description': nameB, 
            'assetId':idasset, 
            'region': regionB, //['coordinates']
            'scale': 10, 
            'maxPixels': 1e13,
            "pyramidingPolicy":{".default": "mode"}
        }
        
    Export.image.toAsset(optExp)
    print("salvando ... " + nameB + "..!");
};


var param = {
    'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
    'asset_geodatin_work': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4',
    'asset_geodatin_next': 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    'asset_maps':'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referencias',
    'carta_selected': "SC-24-V-D",
    'subgrade': 0
};

var regiaoCaat = ee.FeatureCollection(param.subGridsAsset)
                        .filter(ee.Filter.eq("grid", param.carta_selected))
                        .filter(ee.Filter.eq("subgrid_id", param.subgrade))
                        .geometry();
print("SHPs região da carta da Caatinga ", param.carta_selected);
var idAssetBase = 'projects/mapbiomas-arida/coletaMapaRef';
var imgAflor  = afloramento.reduceToImage(['classe'], ee.Reducer.first())
var name_export= 'mascara_area_afloramento_image';
processoExportarImage(imgAflor, name_export, idAssetBase, regiaoCaat);