
var palettes = require('users/mapbiomas/modules:Palettes.js');
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
    planet: {
        'min':14,
        'max':3454,
        // 'gamma':1.8,
        'bands': ['R','G','B']
    },
    visclassCC: {
        "min": 0, 
        "max": 62,
        "palette":  palettes.get('classification7'),
        "format": "png"
    }
};


//exporta a imagem classificada para o asset
var processoExportar = function (ROIsFeat, nameB, idAssetF){

    var assetId = idAssetF + '/' + nameB;
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetId         
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!");
};

var param = {
    'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
    'asset_geodatin_work': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4',
    'asset_geodatin_next': 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    'asset_mapbiomasCol8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'asset_mapbiomasS2': 'projects/mapbiomas-workspace/public/collection_S2_beta/collection_LULC_S2_beta',
    'asset_output': 'projects/mapbiomas-arida/coletaMapaRef',
    'carta_selected': "SC-24-V-D",
    'subgrade': 0
};

var knowPolnumbers = false;
var exportROIs = false;
var periodos = ['seco','chuvoso'];
var showCartaSB24ZD = false;
var yearShow = 2022;
var outline = null;
var recortePlanet = null;
var carta_tmp =  null;

var regiaoCaat = ee.FeatureCollection(param.subGridsAsset)
                        .filter(ee.Filter.eq("grid", param.carta_selected))
                        .filter(ee.Filter.eq("subgrid_id", param.subgrade))
                        .geometry();
print("SHPs região da carta da Caatinga ", param.carta_selected);


var imgColGeodatin = ee.ImageCollection(param.asset_geodatin_next).merge(
                          ee.ImageCollection(param.asset_geodatin_work))
                              .filter(ee.Filter.eq('year', yearShow))
                              .filterBounds(regiaoCaat)
                              .mosaic().clip(regiaoCaat);
print("show image imgColGeodatin", imgColGeodatin);
var mapSentinel = ee.Image(param.asset_mapbiomasS2).clip(regiaoCaat)

periodos.forEach(function(nperiodo){
    if (nperiodo === 'chuvoso'){
        Map.addLayer(imgColGeodatin, vis.mosaic_Median_Wet, "periodo_Wet");
    }else{
        Map.addLayer(imgColGeodatin, vis.mosaic_Median_Dry, "periodo_Dry");
    }
})
Map.addLayer(mapSentinel.select("classification_" + yearShow.toString()),  
                            vis.visclassCC, 'Sentinel '+ yearShow.toString(), false)

// Paint all the polygon edges with the same number and width, display.
var outline = ee.Image().toByte().paint({
                  featureCollection: regiaoCaat, 
                  color: 1,  width: 3 });
Map.addLayer(outline, {palette: 'FF0000'}, param.carta_selected + 'subGride 0');

var allFeatures = formacao_florestal.merge(
                        formacao_savanica).merge(
                            afloramento_rochoso).merge(
                                pastagem).merge(
                                    agricultura).merge(
                                        area_urbanizada).merge(
                                            outras_areas_nao_veg).merge(
                                                corpos_agua);
if (knowPolnumbers === true){
    print("size of polygons collection Formação Florestal ", formacao_florestal);
    print("size of polygons collection Formação Savanica ", formacao_savanica);
    print("size of polygons collection Afloramento Rochoso ", afloramento_rochoso);
    print("size of polygons collection Pastagem ", pastagem);
    print("size of polygons collection Agricultura ", agricultura);
    print("size of polygons collection Área Urbanizada ", area_urbanizada);
    print("size of polygons collection Outras Áreas não Vegetadas ", outras_areas_nao_veg);
    print("size of polygons collection Corpos de Agua ", outras_areas_nao_veg);
}

if (exportROIs === true){
    var nameROIs = "amostras_coletadas_mapa_referencia_2022_S2_v3";
    processoExportar(allFeatures, nameROIs, param.asset_output);
}

// vbersão 3
// https://code.earthengine.google.com/688f500a1029b07950b81e876f8743ce
// versão 3A
https://code.earthengine.google.com/e2070371d1c42472f701175dc074acae