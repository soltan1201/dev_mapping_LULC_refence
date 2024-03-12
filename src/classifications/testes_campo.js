
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
var assetROIsCamp = 'projects/mapbiomas-arida/coletaMapaRef/poligons_area_campestre_points'
var roisCampo = ee.FeatureCollection(assetROIsCamp).map(function(feat){return feat.set('classe', 12)})
print("pontos de campos ", roisCampo.limit(10))
var assetCampGTB = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referencias/mapa_SC-24-V-D_0_2020_GTB_v53_areasCampestres';
var imgCampGTB = ee.Image(assetCampGTB)
var assetCampRF = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referencias/mapa_SC-24-V-D_0_2020_RF_v51_areasCampestres';
var imgCampRF = ee.Image(assetCampRF)

var asset_maps_vector = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_ref_vetorizar';
var imgClassVect = ee.ImageCollection(asset_maps_vector);
print("image Class to Vector", imgClassVect);

var classGTBvect = imgClassVect.filter(ee.Filter.eq('version', '1'))
                        .filter(ee.Filter.eq('classificador', 'filter-GTB'))
                        .first(); 
print("Classification GTB to Vector ", classGTBvect);
Map.addLayer(classGTBvect, vis.visclassCC, 'class GTB vector');
Map.addLayer(imgCampGTB, vis.visclassCC, 'class GTB 53');
Map.addLayer(imgCampRF, vis.visclassCC, 'class RF v1');
Map.addLayer(roisCampo, {color: 'd6bc74'}, 'grassland ROIs', false);

