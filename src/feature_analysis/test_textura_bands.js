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
    mosaic_Contrast_Dry_norm: {
        min: 0.2, 
        max: 3,        
        palette: '87453f,773731,672823,561a16,460b08'
    },
    mosaic_Texture_norm: {
        min: 0.2, 
        max: 3,        
        palette: 'fffec0,f1f0b3,e3e2a6,d5d599,c7c78c' 
    },
    mosaicVarianza_norm:{
        min: 0.2, 
        max: 3,        
        palette: '732472,571b55,3a1239,1d091c,000000'
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

var agregateBandsTexturasGLCM = function(image){
    print("processing agregateBandsTexturasGLCM")        
    var img = ee.Image(image).multiply(10000).toInt32();                

    var texturaNirDry = img.select('nir_median_dry').glcmTexture(3)  
    var savgNirDry = texturaNirDry.select('nir_median_dry_savg').divide(10000).toFloat()  // promedio
    var dissNirDry = texturaNirDry.select('nir_median_dry_diss').divide(1000).toFloat()  // dissimilarity
    var contrastNirDry = texturaNirDry.select('nir_median_dry_contrast').divide(1000000).toFloat() // contrast
    var varNirDry = texturaNirDry.select('nir_median_dry_var').divide(1000000).toFloat()  // varianza
    print(texturaNirDry);
    
    var texturaRedDry = img.select('red_median_dry').glcmTexture(2)  
    var savgRedDry = texturaRedDry.select('red_median_dry_savg').divide(10000).toFloat()
    var dissRedDry = texturaRedDry.select('red_median_dry_diss').divide(1000).toFloat()
    var contrastRedDry = texturaRedDry.select('red_median_dry_contrast').divide(1000000).toFloat()
    var varRedDry = texturaRedDry.select('red_median_dry_var').divide(1000000).toFloat()
    
    var texturaSwir1Dry = img.select('swir1_median_dry').glcmTexture(3) 
    var savgSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_savg').divide(10000).toFloat()
    var dissSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_diss').divide(1000).toFloat()
    var contrastSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_contrast').divide(1000000).toFloat()
    var varSwir1Dry = texturaSwir1Dry.select('swir1_median_dry_var').divide(1000000).toFloat()

    return  image.addBands(savgNirDry).addBands(contrastNirDry
                    ).addBands(savgRedDry).addBands(contrastRedDry
                        ).addBands(savgSwir1Dry).addBands(contrastSwir1Dry)
                        .addBands(dissNirDry).addBands(dissRedDry).addBands(dissSwir1Dry)
                        .addBands(varNirDry).addBands(varRedDry).addBands(varSwir1Dry)
}
var param = {
    'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
    'asset_geodatin_work': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mosaics-CAATINGA-4',
    'asset_geodatin_next': 'projects/nexgenmap/MapBiomas2/SENTINEL/mosaics-CAATINGA-4',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    'asset_gedi': 'users/potapovpeter/GEDI_V27',
    'asset_maps_ref': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_referencias',
    'asset_maps_vector': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_ref_vetorizar',
    'asset_mapa_corregido': 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapa_GTB_mod_S2_refence_2020_v3',
    'asset_Col8': 'projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1',
    'asset_soil': "users/diegocosta/doctorate/SUM_Bare_Soils_Caatinga",
    'carta_selected': "SC-24-V-D",
    'subgrade': 0
};

var yearShow = 2022;
var regiaoCaat = ee.FeatureCollection(param.subGridsAsset)
                        .filter(ee.Filter.eq("grid", param.carta_selected))
                        // .filter(ee.Filter.eq("subgrid_id", param.subgrade))
                        // .geometry();
print("SHPs região da carta da Caatinga ", param.carta_selected);


var imgColGeodatin = ee.ImageCollection(param.asset_geodatin_next).merge(
                          ee.ImageCollection(param.asset_geodatin_work))
                              .filter(ee.Filter.eq('year', yearShow))
                              .filterBounds(regiaoCaat)
                            //   .mosaic().clip(regiaoCaat);
print("show image imgColGeodatin", imgColGeodatin);


var imgColGeodatinNorm = imgColGeodatin.map(normalize_image);
// building a imagem 
imgColGeodatinNorm = imgColGeodatinNorm.mosaic().clip(regiaoCaat);
imgColGeodatin = imgColGeodatin.mosaic().clip(regiaoCaat);

imgColGeodatinNorm =  agregateBandsTexturasGLCM(imgColGeodatinNorm);


Map.addLayer(imgColGeodatinNorm, vis.mosaic_Median_Wet_norm, "periodo_Wet_Norm", false);
Map.addLayer(imgColGeodatinNorm, vis.mosaic_Median_Dry_norm, "periodo_Dry_Norm");
Map.addLayer(imgColGeodatinNorm.select('red_median_dry_contrast'), vis.mosaic_Contrast_Dry_norm, "constrast_Dry_Norm", false);
Map.addLayer(imgColGeodatinNorm.select('nir_median_dry_savg'), vis.mosaic_Texture_norm, "savg_dry_Norm", false);
Map.addLayer(imgColGeodatinNorm.select('nir_median_dry_diss'), vis.mosaic_Texture_norm, "diss_Dry_Norm");
Map.addLayer(imgColGeodatinNorm.select('nir_median_dry_var'), vis.mosaicVarianza_norm, "var_dry_Norm");
// var outline = ee.Image().toByte().paint({
//                   featureCollection: regiaoCaat.filter(ee.Filter.eq("subgrid_id", param.subgrade)), 
//                   color: 1,  width: 3 });
// Map.addLayer(outline, {palette: 'FF0000'}, param.carta_selected + 'subGride 0');


