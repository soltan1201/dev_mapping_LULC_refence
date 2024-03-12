import numpy as np
import cv2
from skimage import io,filters, color, img_as_float, img_as_ubyte
from matplotlib import pyplot as plt
plt.rcParams['image.cmap'] = 'gray'

#Imagen a analizar
#Las fotos de entrada estan en formato png o jpeg
imagenDatosVivos = './Logo.png'

## FILTRO GAUSSIANO
imagenLogo = io.imread(imagenDatosVivos)

#Redimensionamiento de la imagen de entrada
fixed_size = tuple((500, 400))
imagenLogo = cv2.resize(imagenLogo, fixed_size) 

#Gauss
bs0 = filters.gaussian(imagenLogo, sigma=1, multichannel=False)
bs1 = filters.gaussian(imagenLogo, sigma=3, multichannel=False)
bs2 = filters.gaussian(imagenLogo, sigma=5, multichannel=False)
bs3 = filters.gaussian(imagenLogo, sigma=15, multichannel=False)

f, (ax0, ax1, ax2, ax3) = plt.subplots(1, 4, figsize=(16, 5))
ax0.imshow(bs0)
ax0.set_title('$\sigma=1$')
ax1.imshow(bs1)
ax1.set_title('$\sigma=3$')
ax2.imshow(bs2)
ax2.set_title('$\sigma=5$')
ax3.imshow(bs3)
ax3.set_title('$\sigma=15$')
plt.show()

## FILTRO SOBEL Y ROBERTS
imageBlancoNegro = color.rgb2gray(imagenLogo)

edgeRoberts = filters.roberts(imageBlancoNegro)
edgeSobel = filters.sobel(imageBlancoNegro)

sobelV=filters.sobel_v(imageBlancoNegro)
sobelH=filters.sobel_h(imageBlancoNegro)

f, (ax0, ax1, ax2, ax3) = plt.subplots(1, 4, figsize=(16, 5))
ax0.imshow(edgeRoberts)
ax0.set_title('Operador cruzado de Robert')
ax1.imshow(edgeSobel)
ax1.set_title('Operador de Sobel')
ax2.imshow(sobelV)
ax2.set_title('Operador de Sobel vertical')
ax3.imshow(sobelH)
ax3.set_title('Operador de Sobel horizontal')
plt.show()

## FILTRO GAUSSIANO + SOBEL
imagenLogo = cv2.cvtColor(imagenLogo, cv2.COLOR_BGR2GRAY)

bg = cv2.GaussianBlur(imagenLogo, (15, 15), 10)
bc = filters.sobel(imagenLogo)

fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(15, 15))
ax0.imshow(imagenLogo)
ax0.set_title('Original')
ax1.imshow(bg)
ax1.set_title('Filtro Gauss')
ax2.imshow(-bc)
ax2.set_title("Filtros Gauss+Sobel")
plt.show()

## FILTRO LAPLACE, MEDIAN, FRANGI Y PREWITT
laplace = filters.laplace(imageBlancoNegro)
median = filters.median(imageBlancoNegro)
frangi = filters.frangi(imageBlancoNegro)
prewitt = filters.prewitt(imageBlancoNegro)
 
f, (ax0, ax1,ax2, ax3, ax4) = plt.subplots(1, 5, figsize=(16, 5))
ax0.imshow(imagenLogo)
ax0.set_title('Original')
ax1.imshow(frangi)
ax1.set_title('Filtro Frangi')
ax2.imshow(prewitt)
ax2.set_title('Filtro Prewitt')
ax3.imshow(laplace)
ax3.set_title('Filtro Laplace')

ax4.imshow(median)
ax4.set_title('Filtro Median')
plt.show()