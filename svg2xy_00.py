# -*- coding: cp1252 -*-
#
# 19feb16 salvando da inkScape in modo SVG plain il formato è leggibile
#         anche coi file da internet
#
# 25dic15
#
##
##    ID00 a volte non c'è l'ID
##    ID01 il separatore dei campi può essere solo lo spazio
##    uscita inkScape d="M 451.42857,289.50504 C 451.42857,269.50504
##    file da rete donnaInBikini <path fill="#fefefe" d=" M 0.00 0.00 L 786.00 0.00 L 786.00 1234.62   
#     senza virgole compact mode
#     vedi rose (ora c'è un zm53 67 c x,y
##
##    28feb16
##    occorre gestire il fill. senza esso le conversioni di disegni non
##    si capiscono
##
##    06mar16   dimensione immagine in uscita ora rettangolare (dim_fisica_x e y)
##              risolto un pb su operazione penna su
##              agginta selezione file da finestra
##
### init nov15
#--------------------------------------------------------------


import xml.etree.ElementTree as ET
import turtle
from graphics import *

PRINT_OUT = 0
penUpInvisibile = 0



import tkinter as tk
from tkinter import filedialog


root = tk.Tk()
root.withdraw()

# define options for opening or saving a file
file_path = filedialog.askopenfilename(filetypes=[("svg files","*.svg")])

tree = ET.parse(file_path)
#tree = ET.parse('frattali.svg')
#tree = ET.parse('logo.svg')

#tree = ET.parse('procione.svg')
#tree = ET.parse('disegni_pronti/woman-bikini_plain.svg')
#tree = ET.parse('rose_plain.svg')
#tree = ET.parse('empowered-by-gnu.svg')
#tree = ET.parse('rose_01.svg')
#tree = ET.parse('hatch_fill.svg')
#tree = ET.parse('20160228_171931__pathLine__.svg')
root = tree.getroot()


'''
http://eli.thegreenplace.net/2012/03/15/processing-xml-in-python-with-elementtree


...
  <g
     inkscape:label="Livello 1"
     inkscape:groupmode="layer"
     id="layer1">
    <rect
       style="fill:none;stroke:#000000;stroke-opacity:1"
       id="rect2985"
       width="557.14288"
       height="197.14285"
       x="100"
       y="126.6479"
       ry="3.4437015" />
'''

# inizializzati a caso. solo per definire le dimensioni
# sono diversi dagli array di c
px = [66.25, 333, 333, 1]
py = [66.25, 333, 333, 1]

pltx = []
plty = []
pltp = []

# da rivedere
px2mm = 1/3  #130/600
offsetx = -75
offsety = -75


mng_cmds = ['m', 'M', 'l', 'L', 'c', 'C', 'z']


# http://pomax.github.io/bezierinfo/
def Bezier3(t, w):
    t2 = t * t;
    t3 = t2 * t;
    mt = 1-t;
    mt2 = mt * mt;
    mt3 = mt2 * mt;
    return (w[0]*mt3 + 3*w[1]*mt2*t + 3*w[2]*mt*t2 + w[3]*t3);


# apllica la trasformazione corrente
# mette i punti in coda
def appenData(x, y, pen):

    # vedo se c'e' trasformazione
    if 'transform' in elem.attrib:
    
        transform   = elem.attrib['transform']
        transform = transform.replace('matrix', '')
        transform = transform.replace('(', '')
        transform = transform.replace(')', '')
        t = transform.split(',')
        # in ['matrix(0.98914484,-0.14694383,0.14694383,0.98914484,-274.15788,-407.43941)']
        # out['0.98914484', '-0.14694383', '0.14694383', '0.98914484', '-274.15788', '-407.43941']

        Xt = float(t[0])*x + float(t[2])*y + float(t[4])
        Yt = float(t[1])*x + float(t[3])*y + float(t[5])
            
    else:
        Xt = x
        Yt = y
    
    pltx.append(Xt)
    plty.append(Yt)    
    pltp.append(pen)


    

#
# rect rettangolo ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
for elem in tree.iter(tag='{http://www.w3.org/2000/svg}rect'):
#for elem in tree.iter():
#    print (elem.tag , elem.attrib['width'])
#    print (elem.attrib['id'], elem.attrib['width'], elem.attrib['height'], elem.attrib['x'], elem.attrib['y'])

    print('rect')
    print("elemento id: ", elem.attrib['id'])

    ''' gli angoli sono
        x, y
        x + width, y + heigth
        x, y + heigth
    '''
    idr= elem.attrib['id']




    w = float(elem.attrib['width'])
    h = float(elem.attrib['height'])
    x = float(elem.attrib['x'])
    y = float(elem.attrib['y'])

    print(idr)
    print(x,   ',', y)
    print(x+w, ',', y)
    print(x+w, ',', y+h)
    print(x  , ',', y+h)

    pen = 1;
    appenData(x, y, pen)
    appenData(x+w, y, pen)
    appenData(x+w, y+h, pen)
    appenData(x, y+h, pen)
    

#
# path +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 
for elem in tree.iter(tag='{http://www.w3.org/2000/svg}path'):
#for elem in tree.iter():
    '''
        elem.attrib['d']
        http://www.tutorialspoint.com/python/string_split.htm

        minuscole per elementi relativi
        m sta per elementi relativi

        M x y = Move the pen to x y.
        L x y = Draw a line to x y.

        C bezier ??

        z = Close path. Draw a line to the beginning point.

        http://xahlee.info/js/svg_path_spec.html
        http://www.w3.org/TR/SVG/paths.html#PathDataCubicBezierCommands
    '''

    modo = ''
    first = 0
    firstMove = 0

    # dovrò trattare questi elementi
    print('path')
    
# ID00   a volte id non c'è !! print("elemento id: ", elem.attrib['id'])

    # vedi ID01
    
    listaPunti = elem.attrib['d']

    '''

    Cubic Bézier commands (C, c, S and s). A cubic Bézier segment is
    defined by a start point, an end point, and two control points.
    '''
    # nel caso non vi siano spazi non riesce a fare lo split
    # aggiungo degli spazi ai comandi in ogni caso
    # devo farlo per tutti i comandi
    
    listaPunti = listaPunti.replace("L", " L ")
    listaPunti = listaPunti.replace("M", " M ")

    a=listaPunti.split()    # diventa ['105.71429,158.07647', '445.71428,0', '0,240', '-445.71428,-194.28572', '0,-48.57143']

    
    x = y = 0               # init punto iniziale
    j = 0
    for i in range(0, len(a)):
        
        if (PRINT_OUT):
            print("a[i]: ",a[i])
            
        # testo se la lettera è un comando
        if   ((a[i])=='m'):
            modo = 'rel'
            cmd  = a[i];
            print (modo)
        elif ((a[i])=='M'):
            modo = 'abs'
            cmd  = a[i];
            print (modo)
        elif ((a[i])=='l'):     # linea relativa
            modo = 'rel'
            cmd  = a[i];
            print (modo)
        elif ((a[i])=='L'):     # linea abs
            modo = 'abs'
            cmd  = a[i];
            print (modo)
        elif ((a[i])=='z' or (a[i])=='Z'):
            x = x0;
            y = y0;
            cmd  = a[i];
            print ('zero')
        elif ((a[i])=='C'):
            modo = 'abs'
            cmd  = a[i];
            arg  = 0;
        elif ((a[i])=='c'):
            modo = 'rel'
            cmd  = a[i];
            arg  = 0;
        elif ((not a[i][0].isalpha) and (not(a[i][0] in mng_cmds)) ):
            print("**************************")
            print("cmd non trattato: ", a[i])
            print("**************************")
        else:
            # analizzo gli argomenti in base a cmd e argoemnti
            # comando moveTo o lineTo
            # hanno un solo argomento
            if (cmd == 'm' or cmd == 'M'):
                # penna su
                if (firstMove == 0):
                    pen  = 0
                    firstMove = 1
                else:
                    pen  = 0
                if (modo == 'rel'):
                    x = x + float(a[i].split(',')[0])
                    y = y + float(a[i].split(',')[1])
                else:
                    x = float(a[i].split(',')[0])
                    y = float(a[i].split(',')[1])

                appenData(x, y, pen)


            if (cmd == 'l' or cmd == 'L'):
                # penna giu
                pen  = 1;
                if (modo == 'rel'):
                    x = x + float(a[i].split(',')[0])
                    y = y + float(a[i].split(',')[1])
                else:
                    x = float(a[i].split(',')[0])
                    y = float(a[i].split(',')[1])

                appenData(x, y, pen)


            # comando c o C / s/ S
            # hanno 3 argomenti. il punto iniziale è il valore corrente
            # la prima volta che passo da qui dopo il comando
            # devo settare sia Pi che PcontrolloInit
            if (cmd == 'c' or cmd == 'C'):
                pen  = 1;
                #print("a[i]", a[i])
                if (modo == 'rel'): # and (arg <= 3)):
                    if (arg == 0):
                        px[0] = x
                        py[0] = y
                        px[1] = px[0] + float(a[i].split(',')[0])
                        py[1] = py[0] + float(a[i].split(',')[1])
                        arg = 1
                    else:
                        px[arg] = px[0] + float(a[i].split(',')[0])
                        py[arg] = py[0] + float(a[i].split(',')[1]);
                else:# assoluto
                    if (arg == 0):
                        px[0] = x
                        py[0] = y
                        px[1] = float(a[i].split(',')[0])
                        py[1] = float(a[i].split(',')[1])
                        arg = 1
                    else:
                        px[arg] =float(a[i].split(',')[0])
                        py[arg] =float(a[i].split(',')[1])

                arg = arg +1

                if (arg == 4):
                    # p[0] punto iniziale, p[1] è controllo iniziale, p[2] controllo finale, p[3] punto finale
                    t = 0
                    #print (px)
                    #print (py)
                    while (t < 1):
                        x = Bezier3(t, px)
                        y = Bezier3(t, py)
                        #line(xo,yo, x,y)
                        xo = x
                        yo = y
                        #print(t, '-', x, ',', y)

                        appenData(x, y, pen)

                        t= t + 0.1

                    x = Bezier3(1, px)
                    y = Bezier3(1, py)
                    #line(xo,yo, x,y)
                    xo = x
                    yo = y
                    #print(1, '-', x, ',', y)

                    # se seguono anltri punti setto Pi
                    # altrimenti se c'è un comando domina lui
                    arg=1    # indica che Pi gia fatto
                    px[0] = x
                    py[0] = y


        if (first == 0):
            x0 = x
            y0 = y
            first = 1




#    print (listaPunti)
#    print (elem.tag , elem.attrib['id'], elem.attrib['d'])
#    print (elem.attrib['id'], elem.attrib['width'], elem.attrib['height'], elem.attrib['x'], elem.attrib['y'])



xmax = ymax = -10000
xmin = ymin =  10000
#controlla valori di max e min di x e y
#per trovare centratura
for i in  range(len(pltx)):
    if (i > 1):
        if (pltx[i] < xmin):
            xmin = pltx[i]
        if (pltx[i] > xmax):
            xmax = pltx[i]
        if (plty[i] < ymin):
            ymin = plty[i]
        if (plty[i] > ymax):
            ymax = plty[i]
    

# voglio i disegno centrato intorno allo zero
# quindi metto offset = (max + min)/2

offsetx = (xmax + xmin)/2
offsety = (ymax + ymin)/2

# faccio una scalatura tale da avere al più 150 mm rispetto allo zero

print("xmin: ", xmin, " xmax: ", xmax)
print("ymin: ", ymin, " ymax: ", ymax)

# faccio tavola di uscita retteangolare
dim_mm_x = 250*2
dim_mm_y = 350*2


massimo_x = xmax - xmin
massimo_y = ymax - ymin

px2mm_lungo_x = dim_mm_x/massimo_x
px2mm_lungo_y = dim_mm_y/massimo_y

if (px2mm_lungo_x < px2mm_lungo_x):
    px2mm = px2mm_lungo_x
else:
    px2mm = px2mm_lungo_y
    



f1=open('./xy.txt', 'w')
for i in  range(len(pltx)):
    # converti misure to mm *px2mm
    xmm = (pltx[i] - offsetx)*px2mm
    ymm = (plty[i] - offsety)*px2mm
    # points[0].x = -50;
    print(xmm, ';',ymm, ';', pltp[i], file=f1)


f1.close()
print ("fine file")



print ("inizia disegno")



zoom = 1;
xM   = 1000;
yM   =  800;

#1 xM   = massimo_x;   # dimensiooni in pixel
#1 yM   = massimo_y;

print("offset  x, y [px]: ", offsetx, offsety)
print("massimox,px y[px]: ", massimo_x, massimo_y)
print("px2mm            : ", px2mm)

#finestra con dimensioni limite [px]
#1win = GraphWin('simulation', massimo_x* 1.1*px2mm, massimo_y* 1.1*px2mm)
win = GraphWin('simulation', xM, yM)

pt = Point(0,0)
pt.draw(win)

#turtle.speed(9)


for i in  range(len(pltx)):

    nextPt = Point(((pltx[i] - offsetx)*px2mm)*zoom + xM/2, ((plty[i] - offsety)*px2mm )*zoom + yM/2)
#1    nextPt = Point(((pltx[i] - offsetx))*zoom + xM/2, ((plty[i] - offsety))*zoom + yM/2)
    line = Line(pt, nextPt)
    if (penUpInvisibile == 1) and (pltp[i] == 1):
        line.draw(win)
        line.setOutline('black')

    if (penUpInvisibile == 0):
        line.draw(win)
        if (pltp[i] == 1):
            line.setOutline('black')
        else:
            line.setOutline('red')

    pt = nextPt

print ("fine disegno")

