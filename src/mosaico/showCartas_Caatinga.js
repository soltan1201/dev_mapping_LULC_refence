var vis = {
    planet: {
        'min':14,
        'max':3454,
        // 'gamma':1.8,
        'bands': ['R','G','B']
    }
};

var param = {
    'subGridsAsset': 'projects/nexgenmap/ANCILLARY/nextgenmap_subgrids',
    'cartasCaat': ["SB-24-Z-D", "SC-24-V-D"],
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas'
    
};
var showCartaSB24ZD = false;
var yyear = 2022;
var outline = null;
var nameCarta = null
var recortePlanet = null;
var carta_tmp =  null;

var cartasCaat = ee.FeatureCollection(param.subGridsAsset)
                      .filter(ee.Filter.inList("grid", param.cartasCaat));
print("SHPs das cartas da Caatinga ", cartasCaat);

// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI);
// Filter basemaps by date and get the first image from filtered results
var basemap2016 = nicfi.filter(ee.Filter.date('2022-12-01','2023-01-01'));
var img = ee.Image.constant(8).unmask()

if (showCartaSB24ZD){
    nameCarta = "SB-24-Z-D";
    print("show Carta  " + nameCarta);
    carta_tmp = cartasCaat.filter(ee.Filter.eq("grid", nameCarta))//.bounds();
    recortePlanet = basemap2016.first().clip(carta_tmp.geometry());
    
}else{
    nameCarta = "SC-24-V-D";
    print("show Carta " + nameCarta);
    carta_tmp = cartasCaat.filter(ee.Filter.eq("grid", nameCarta))//.bounds();
    recortePlanet = basemap2016.first().clip(carta_tmp.geometry()) 
  
}

Map.addLayer(carta_tmp)
Map.addLayer(recortePlanet, vis.planet, "planet");
// Paint all the polygon edges with the same number and width, display.
outline = ee.Image().toByte().paint({
                  featureCollection: carta_tmp, 
                  color: 1,  width: 3 });
Map.addLayer(outline, {palette: 'FF0000'}, nameCarta);


