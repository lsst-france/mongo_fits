# mongo_fits

Study package to evaluate the collaboration between FITS and MongoDb

les traces d'exécution de la démo LSST avec les versions v10.1 et v11.0 du stack sont en ligne:

  https://github.com/airnandez/cluefs-tools

Vous y trouverez entre autres des fichiers .csv qui contiennent l'information de l'activité I/O induite par la démo. L'outil de collecte est clueFS: 

  https://github.com/airnandez/cluefs

Le format du fichier de trace généré par clueFS est aussi documenté:

  https://github.com/airnandez/cluefs/blob/master/doc/EventFormats.md


------------------------------------------

Algo to convert RA DEC into pixel coordinates

we consider header the following fields

CRPIX1  CRPIX2
CRVAL1  CRVAL2
CD1_1  CD1_2
CD2_1  CD2_2

RA  in [0 … 360]   degrés   modulo 360
DEC in [-90 … 90]  degrés

dX = X - CRPIX1
dY = Y - CRPIX2

RA =  (CD1_1 * dX + CD1_2 * dY) + CRVAL1
DEC = (CD2_1 * dX + CD2_2 * dY) + CRVAL2

inverting it gives:

x = (dc - af) / (bd - ae)
y = (bf - ec) / (bd - ae)

x = X - CRPIX1
y = Y - CRPIX2
a = CD1_1
b = CD1_2
c = RA - CRVAL1
d = CD2_1
e = CD2_2
f = DEC - CRVAL2


