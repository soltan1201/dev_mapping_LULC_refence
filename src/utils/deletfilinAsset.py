import ee
import sys
try:
    ee.Initialize()
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise



asset = 'projects/mapbiomas-workspace/AMOSTRAS/col8/CAATINGA/mapas_ref_vetorizar'
listSB = ee.ImageCollection(asset).filter(                        
                            ee.Filter.eq('version', '10'))

 
lsNome = listSB.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()

# print "eliminando mes {}".format(mess)
print (" e {} imagens ".format(len(lsNome)))

# cont = 1
for cc, feat in enumerate(lsNome[:]):  
    path_ = str(asset + '/' + feat)
    print ( path_)
    print ("try to remove ... item {} ".format(cc))
    try:
        # ee.data.deleteAsset(path_)  
        pass
    except:
        print("don't exits ")