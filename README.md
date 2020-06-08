# etereo_plotter_verticale
un plotter verticale "leggero".

Il file "svg2xy.py" legge un file svg lo converte in coordinate xy. Le coordinate sono accodate in un file per essere lette dalla scheda Arduino. Il software legge solo alcune primitive. E' stato un utile esercezion per capire la struttura dei file SVG. 


Il "Vplotter_02_commentata.ino" gira su Arduino. Legge un file dalla SD card e muove gli stepper di conseguenza. Le coordiante cartesiane vengono trasformate in lunghezze dei cavi.




Plotter verticale_21ago16.pdf 	descrizione del progetto
Vplotter_02_commentata.ino 	    parte su Arduino
plotterVertical_01.fzz 	        schema elettrico in Fritzing
plotterVertical_01_bb.png 	    disegno del circuito in Gritzing
procione.svg 	                  disegno di esempio
svg2xy_00.py                    parser di file .svg per Etereo.


# link ai post

https://stuffcube.wordpress.com/2016/03/12/etereo-un-plotter-verticale-costruibile-sul-tavolo-della-cucina/
https://stuffcube.wordpress.com/2016/03/19/etereo-un-plotter-verticale-costruibile-sul-tavolo-della-cucina-parte-2/
