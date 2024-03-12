//exporta a imagem classificada para o asset
var processoExportar = function (ROIsFeat, nameB){
    var idAssetF = 'projects/mapbiomas-arida/coletaMapaRef'
    var assetId = idAssetF + '/' + nameB;
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetId         
        };
    Export.table.toAsset(optExp);
    print("salvando ... " + nameB + "..!");
};

var randomSample = function(feat){
                        var pmtros = {
                            region: feat.geometry(), 
                            points: 30, 
                            seed: 0, 
                            maxError: 0.01
                        };
                        var ptos = ee.FeatureCollection.randomPoints(pmtros);                        
                        var new_ROIs = ptos.map(
                                            function(nfeat){
                                                return nfeat.set('classe', feat.get('classe'));
                                          });
                        return new_ROIs;
                    };
var asset_ROIsv2 = 'projects/mapbiomas-arida/coletaMapaRef/amostras_coletadas_mapa_referencia_2022_S2_v2';
var asset_ROIsv3 = 'projects/mapbiomas-arida/coletaMapaRef/amostras_coletadas_mapa_referencia_2022_S2_v3';

var featROIsv2 = ee.FeatureCollection(asset_ROIsv2);
var featROIsv3 = ee.FeatureCollection(asset_ROIsv3);

print("poligons from versão 2", featROIsv2.limit(5));
print("size featCollections pontos ", featROIsv2.size());
print("poligons from versão 3", featROIsv3.limit(5));
print("size featCollections pontos ", featROIsv3.size());

var ptosROIsv2 = featROIsv2.map(randomSample);
var ptosROIsv3 = featROIsv3.map(randomSample);

ptosROIsv2 = ptosROIsv2.flatten();
ptosROIsv3 = ptosROIsv3.flatten();
print("pontos from versão 2", ptosROIsv2.limit(3));
print("with size ", ptosROIsv2.size());
print("pontos from versão 3", ptosROIsv3.limit(5));
print("with size ", ptosROIsv3.size());

var newName_ROIsv2 = 'amostras_ptos_samples_mapa_referencia_2022_S2_v2';
var newName_ROIsv3 = 'amostras_ptos_samples_mapa_referencia_2022_S2_v3';

// exportando  os ROIs 
processoExportar(ptosROIsv2, newName_ROIsv2);
processoExportar(ptosROIsv3, newName_ROIsv3);