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
    mosaic_Median_Wet_norm: {
        min: 0.2, 
        max: 1.0,
        bands: ["red_median_wet","green_median_wet","blue_median_wet"]
    },
    mosaic_Median_Dry_norm: {
        min: 0.2, 
        max: 1,
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
var lst_bnd = [
    "blue_median_wet","green_median_wet","red_median_wet",
    "nir_median_wet","swir1_median_wet","swir2_median_wet",
    "blue_median_dry","green_median_dry","red_median_dry",
    "nir_median_dry","swir1_median_dry","swir2_median_dry" 
];
var dict_stat_bnd= {
    "median_blue_median_wet": 1096.0578160344407,
    "median_green_median_wet": 1098.709489027003,
    "median_red_median_wet": 976.5168696816625,
    "median_nir_median_wet": 2488.803981135233,
    "median_swir1_median_wet": 2590.708057737918,
    "median_swir2_median_wet": 1491.7623228609739,
    "median_blue_median_dry": 1172.7243955891456,
    "median_green_median_dry": 1169.1687031130916,
    "median_red_median_dry": 1279.6717378018277,
    "median_nir_median_dry": 2019.8880081974671,
    "median_swir1_median_dry": 3143.650563677744,
    "median_swir2_median_dry": 2093.1297194020954,
    "stdDev_blue_median_wet": 216.81962108751355,
    "stdDev_green_median_wet": 259.92685500367475,
    "stdDev_red_median_wet": 375.5613485310523,
    "stdDev_nir_median_wet": 438.60626940637314,
    "stdDev_swir1_median_wet": 513.3187279778745,
    "stdDev_swir2_median_wet": 466.0627768106192,
    "stdDev_blue_median_dry": 142.54110653132767,
    "stdDev_green_median_dry": 215.4591413723328,
    "stdDev_red_median_dry": 346.9520939981621,
    "stdDev_nir_median_dry": 451.598842719077,
    "stdDev_swir1_median_dry": 577.197374855401,
    "stdDev_swir2_median_dry": 498.71129520994134   
}
var normalize_image = function(image){
    var imgNorm = image.select(["blue_median_wet"]).lt(-1).rename("constant");
    lst_bnd.forEach(function(bnd){
        var medianBnd = dict_stat_bnd["median_" + bnd]
        var stdDevBnd = dict_stat_bnd["stdDev_" + bnd];
        //  calcZ = (arrX - xmean) / xstd;
        var calcZ = image.select(bnd).subtract(ee.Image.constant(medianBnd))
                            .divide(ee.Image.constant(stdDevBnd));
        //     expBandAft =  np.exp(-1 * calcZ)
        var expBandAft = calcZ.multiply(ee.Image.constant(-1)).exp();
        //     return 1 / (1 + expBandAft)
        var bndend = expBandAft.add(ee.Image.constant(1)).pow(ee.Image.constant(-1));
        imgNorm = imgNorm.addBands(bndend.rename(bnd));
    })
    return imgNorm.toFloat().select(lst_bnd)
}

var param = {
    'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
    'asset_geodatin_work': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4',
    'asset_geodatin_next': 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    'asset_gedi': 'users/potapovpeter/GEDI_V27',
    'asset_maps_refV2': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referenciasV2',
    'asset_maps_ref': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referencias',
    'asset_maps_vector': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_ref_vetorizar',
    'asset_mapa_corregido': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapa_GTB_mod_S2_refence_2020_v3',
    'asset_Col8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'asset_soil': "users/diegocosta/doctorate/SUM_Bare_Soils_Caatinga",
    'asset_Drenagem': "projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/DrenagemGTcaatinga",
    'asset_ag_perene': "users/agrosatelite_mapbiomas/CARTAS_NEXTGEN_REFMAP/Carta_Caatinga_perene_v0",
    'asset_ag_temporaria': "users/agrosatelite_mapbiomas/CARTAS_NEXTGEN_REFMAP/Carta_Caatinga_temporaria_v0",
    'asset_urbano': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/layers_urbano',
    'asset_building': 'GOOGLE/Research/open-buildings/v3/polygons',
    'asset_output':  "projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/REF",
    'carta_selected': "SC-24-V-D",
    'subgrade': 0
};

var dictPeriodo = {
    'trimestre_1': ['2022-01-01', '2022-04-01'],
    'trimestre_2': ['2022-04-01', '2022-07-01'],
    'trimestre_3': ['2022-07-01', '2022-10-01'],
    'trimestre_4': ['2022-10-01', '2023-01-01']
};
var lst_trim_planet = ['trimestre_1','trimestre_2','trimestre_3','trimestre_4'];
var showCartaSB24ZD = false;
var yearShow = 2022;
var outline = null;
var recortePlanet = null;
var carta_tmp =  null;
var version = '5';
var exportar = true;
var regiaoCaat = ee.FeatureCollection(param.subGridsAsset)
                        .filter(ee.Filter.eq("grid", param.carta_selected))
                        // .filter(ee.Filter.eq("subgrid_id", param.subgrade))
                        // .geometry();
print("SHPs região da carta da Caatinga ", param.carta_selected);
var mapBiomasCol8 = ee.Image(param.asset_Col8).select('classification_2020').clip(regiaoCaat)
var layerWater = mapBiomasCol8.eq(33).focal_max(5).gt(0);

var imgColGeodatin = ee.ImageCollection(param.asset_geodatin_next).merge(
                          ee.ImageCollection(param.asset_geodatin_work))
                              .filter(ee.Filter.eq('year', yearShow))
                              .filterBounds(regiaoCaat)
                            //   .mosaic().clip(regiaoCaat);
print("show image imgColGeodatin", imgColGeodatin);

var maskGedi = ee.ImageCollection(param.asset_gedi).mosaic().clip(regiaoCaat);

var imgColGeodatinNorm = imgColGeodatin.map(normalize_image);
// building a imagem 
imgColGeodatinNorm = imgColGeodatinNorm.mosaic().clip(regiaoCaat);
imgColGeodatin = imgColGeodatin.mosaic().clip(regiaoCaat);


var date_start = dictPeriodo['trimestre_4'][0];
var date_end = dictPeriodo['trimestre_4'][1];
print("filtrando as imagens entre " + date_start + " e " + date_end);

// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI); 
// Filter basemaps by date and get the first image from filtered results
recortePlanet = nicfi.filter(ee.Filter.date(date_start, date_end))
                        .median().clip(regiaoCaat);
                        
// mapa de referencia de toda a carta 
var mapRefeCartGTBV0 = ee.ImageCollection(param.asset_maps_refV2)
                          .filter(ee.Filter.eq('version', '1')) 
                          .filter(ee.Filter.eq('classificador', 'GTB')) 
                          
// mapa de referencia de toda a carta 
var mapRefeCartRFV0 = ee.ImageCollection(param.asset_maps_refV2)
                          .filter(ee.Filter.eq('version', '2')) 
                          .filter(ee.Filter.eq('classificador', 'RF')) 
                          
print("Numero de imagens by subgrade GTB", mapRefeCartGTBV0);
print()
mapRefeCartGTBV0 = mapRefeCartGTBV0.max();                    

var imgClassVect = ee.ImageCollection(param.asset_maps_vector)
print("image Class to Vector", imgClassVect)


var classRFvect = imgClassVect.filter(ee.Filter.eq('version', '1'))
                        .filter(ee.Filter.eq('system:index', 'mapa_RF_mod_S2_refence_2020'))
                        .first(); 
print("Classification RF to Vector ", classRFvect);
var classModGTB = imgClassVect.filter(ee.Filter.eq('version', '2'));
var mapa_corregido = ee.Image(param.asset_mapa_corregido);

var bare_soil= ee.Image(param.asset_soil).clip(regiaoCaat);
bare_soil = bare_soil.gt(0);
var DrenagemGTcaatinga = ee.FeatureCollection(param.asset_Drenagem);
DrenagemGTcaatinga = DrenagemGTcaatinga.map(
                                function(dd){
                                    return dd.set('classe', 1);    
                            });
DrenagemGTcaatinga = DrenagemGTcaatinga.reduceToImage({
                                            properties: ['classe'], 
                                            reducer: ee.Reducer.first()
                                        });

var layer_Ag_per =  ee.Image(param.asset_ag_perene);
var layer_Ag_temp =  ee.Image(param.asset_ag_temporaria);
var layers_urbano = ee.ImageCollection(param.asset_urbano).max();

var pastagem = mapRefeCartGTBV0.eq(15).multiply(15);
var savana = mapRefeCartGTBV0.eq(4);
var campo = mapRefeCartGTBV0.eq(12);
var floresta = mapRefeCartGTBV0.eq(3);
var waterMask = mapRefeCartGTBV0.eq(33).multiply(4);
var classJoins = pastagem.where(savana.eq(1), 4);
waterMask = waterMask.where(layerWater.eq(1).and(waterMask.eq(4)), 33)

classJoins = classJoins.where(campo.eq(1), 12);
classJoins = classJoins.where(layers_urbano.eq(1), 24);
classJoins = classJoins.where(layer_Ag_per.eq(1), 36);
classJoins = classJoins.where(layer_Ag_temp.eq(1), 19);
floresta = floresta.multiply(4).where(DrenagemGTcaatinga.eq(1).and(floresta.gt(0)), 3);
classJoins = classJoins.where(floresta.gt(0), floresta);
classJoins = classJoins.where(bare_soil.eq(1), bare_soil.eq(1).multiply(25));
classJoins = classJoins.where(waterMask.gt(0), waterMask);

Map.addLayer(recortePlanet, vis.planet, "mosaic_" + 'trimestre_4');
// Map.addLayer(imgColGeodatinNorm, vis.mosaic_Median_Wet_norm, "periodo_Wet_Norm");
Map.addLayer(imgColGeodatinNorm, vis.mosaic_Median_Dry_norm, "periodo_Dry_Norm");
Map.addLayer(waterMask.selfMask(), vis.visclassCC, 'water');
Map.addLayer(mapRefeCartGTBV0, vis.visclassCC, 'class GTB carta V1');
Map.addLayer(classJoins, vis.visclassCC, 'classJoins Merge');
print("class joins ", classJoins)
Map.addLayer(bare_soil.selfMask(), {palette: ["yellow", "red"]}, "Solo Total", false);
Map.addLayer(layer_Ag_per.selfMask(), {palette: ["ffb8f3"]}, "Agro Perene", false);
Map.addLayer(layer_Ag_temp.selfMask(), {palette: ["bb5257"]}, "Agro Temporaria", false);
Map.addLayer(layers_urbano.selfMask(), {palette: ["D4271E"]}, "Layer Urbano", false);

var outline = ee.Image().toByte().paint({
                  featureCollection: regiaoCaat.filter(ee.Filter.eq("subgrid_id", param.subgrade)), 
                  color: 1,  width: 3 });
var outline2 = ee.Image().toByte().paint({
                  featureCollection: DrenagemGTcaatinga, 
                  color: 1,  width: 1 });
Map.addLayer(outline2.selfMask(), {palette: ["blue", "cyan"]}, "Drenagem")
Map.addLayer(outline, {palette: 'FF0000'}, param.carta_selected + 'subGride 0');


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

    var optExpD = {
        'image': imageMap, 
        'description': nameB, 
        'folder': 'Mapa_REF', 
        'region': regionB, //['coordinates']
        'scale': 10, 
        'maxPixels': 1e13    
    }
    
    Export.image.toDrive(optExpD)
    print("salvando ... " + nameB + "..!");


};


var recorteExpor = regiaoCaat.filter(ee.Filter.eq("subgrid_id", 3))
Map.addLayer(recorteExpor, {color: 'yellow'}, 'recorte')
if (exportar){
    classJoins = classJoins.clip(recorteExpor.geometry()).set(
        'classificador', 'filter-GTB',
        'version', '3',
        'biome', 'CAATINGA',
        'collection', 'beta',
        'sensor', 'sentinel',
        'source', 'geodatin'
    )
    print("o mapa será salvo em ", param['asset_output'])
    processoExportarImage(classJoins, 'mapa_GTB_mod_S2_refence_2020_v3Q3', param['asset_output'], recorteExpor.geometry());

}