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
    },
    visGeDi: {
        "min": 0, 
        "max": 17,
        "palette":  [
            'c7ffb4','a5de94','84bd74','2b7e1f',
            '206118','164510','0b2808','000c00'
        ],
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
    'asset_maps': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referencias',
    'asset_maps_toVector': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_ref_vetorizar',
    'inAssetROIsPolg': 'projects/mapbiomas-arida/coletaMapaRef',
    'assetMask_campos': 'projects/mapbiomas-arida/coletaMapaRef/mascara_areas_campestre_image',
    'carta_selected': "SC-24-V-D",
    'subgrade': 0
};
var dictPeriodo = {
    'trimestre_1': ['2022-01-01', '2022-04-01'],
    'trimestre_2': ['2022-04-01', '2022-07-01'],
    'trimestre_3': ['2022-07-01', '2022-10-01'],
    'trimestre_4': ['2022-10-01', '2023-01-01']
};
var showCartaSB24ZD = false;
var yearShow = 2022;
var outline = null;
var recortePlanet = null;
var carta_tmp =  null;
var version = '5';
var exportar = true;
var regiaoCaat = ee.FeatureCollection(param.subGridsAsset)
                        .filter(ee.Filter.eq("grid", param.carta_selected))
                        .filter(ee.Filter.eq("subgrid_id", param.subgrade))
                        .geometry();
print("SHPs região da carta da Caatinga ", param.carta_selected);

var imgColGeodatin = ee.ImageCollection(param.asset_geodatin_next).merge(
                            ee.ImageCollection(param.asset_geodatin_work))
                                .filter(ee.Filter.eq('year', yearShow))
                                .filterBounds(regiaoCaat)
                            //   .mosaic().clip(regiaoCaat);
print("show image imgColGeodatin", imgColGeodatin);

var imgClass = ee.ImageCollection(param.asset_maps)
var classRF = imgClass.filter(ee.Filter.eq('version', version))
                        .filter(ee.Filter.eq('classificador', 'RF'))
                        //.max();
print("Imagens da classificação ", classRF)
classRF = classRF.max()


var classGTB = imgClass.filter(ee.Filter.eq('version', version))
                        .filter(ee.Filter.eq('classificador', 'GTB')); 
                        
print("Imagens da classificação GTB", classGTB);
classGTB = classGTB.max();

// projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_ref_vetorizar/mapa_GTB_mod_S2_refence_2020
var nameRFmod = 'mapa_RF_mod_S2_refence_2020';
var classRFmod = ee.Image(param.asset_maps_toVector + '/' + nameRFmod);
var nameGTBmod = 'mapa_GTB_mod_S2_refence_2020';
var classGTBmod = ee.Image(param.asset_maps_toVector + '/' + nameGTBmod);

var imgColGeodatinNorm = imgColGeodatin.map(normalize_image);
// building a imagem 
imgColGeodatinNorm = imgColGeodatinNorm.mosaic().clip(regiaoCaat);

// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI);
var date_start = dictPeriodo['trimestre_4'][0];
var date_end = dictPeriodo['trimestre_4'][1];
print("filtrando as imagens entre " + date_start + " e " + date_end);
    
// Filter basemaps by date and get the first image from filtered results
recortePlanet = nicfi.filter(ee.Filter.date(date_start, date_end))
                        .median().clip(regiaoCaat);

//http://glad-forest-alert.appspot.com/
var gedi = ee.ImageCollection(param.asset_gedi)
                      .mosaic().clip(regiaoCaat);

// Know minimum and maximum values in images 
var pmtros = {
    reducer: ee.Reducer.minMax(), 
    geometry: regiaoCaat, 
    scale: 300, 
    bestEffort: true, 
    maxPixels: 1e13, 
    tileScale: 8
};
var reduMax = gedi.reduceRegion(pmtros)
print(" Show maximum values ", reduMax);
var mascaraCampo = ee.Image(param.assetMask_campos);

Map.addLayer(recortePlanet, vis.planet, "mosaic_" + 'trimestre_4');
Map.addLayer(imgColGeodatinNorm, vis.mosaic_Median_Dry_norm, "periodo_Dry_Norm");
Map.addLayer(classRF, vis.visclassCC, 'class RF v' + version);
Map.addLayer(classRFmod, vis.visclassCC, 'class RF mod v1');
Map.addLayer(classGTB, vis.visclassCC, 'class GTB ' + version);
Map.addLayer(classGTBmod, vis.visclassCC, 'class GTB mod v1');
Map.addLayer(gedi.updateMask(gedi.gt(0)), vis.visGeDi, "GEDI reclass");
Map.addLayer(mascaraCampo, {min: 0, max: 1}, "mascara Campo");


