/*
 * simple v plotter
 * giorgio323@gmail.com
 * infostuffcube@gmail.com
 * 
 * 29dic15	aggiunta lettura da file
 * 31dic15  aggiunto servo per gestione penna
 * 27feb15  versione grossa. modificato movimento sollevamento e dimensioni

 */

#include <SPI.h>
#include <SD.h>
#include <Servo.h> 

Servo myservo;          // create servo object to control a servo 

#define  TEST_XY        0		// testa posizioni xy
#define  TEST_PENNA     1		// testa movimento penna
#define  ARRAY          2		// muove su un array di punti
#define  FILE           3		// legge xy da file

int mode = FILE;

// definisce la velocità del movimento
#define PDURATION 1000    //1500


// card pin definition						
#define	SD_CS		10		// SD car cs pin
#define SERVO_PIN   9    	// Digital IO pin connected to the servo pin.

// pin per pilotaggio stepper
#define  stepPinA   4
#define  stepPinB   6
#define  dirPinA    3
#define  dirPinB    5


// posizioni servo sollevamento penna
// 1000 + 500*alfa/90 
#define PEN_UP      1200//1130            //  60
#define PEN_DW      1500// 700            //  20°

// nome file di ingresso
#define	NOME_FILE	"xy.txt"

File dataFile;
 
 
long int act_a, act_b;          // posizione corrente

// STEP_EQ sono gli STEP_EQuivalenti del motore passo passo.
// il numero è dato dai passi del motore moltiplicato
// per il microstepping usato
// in questo caso
// programmato driver per avere 8 mcrostep
// gli step sono 20 per giro -> 160 step equivalenti
#define   STEP_EQ     160       // step * ustepRes 20*8

struct point{
    float x;
    float y;
};

// un array di punti usato nel modo ARRAY
struct point points[50];

float x, y, pen;


/* logica e costanti costanti meccaniche
 *
 * ci sono due insiemi di coordinate. 
 * assoluta: ha per orgine il supporto sinistro del filo. 
	xabs cresce da sx verso dx
	yabs cresce verso il basso
	da queste si calcola la lunghezza dei fili
 *
	relativa al centro x0, y0
 * x0 e y0 (rispetto all'assoluto) sono il punto di origine per il disegno (che ha quindi origine nel mezzo)
 * x  e y  sono le coordinate del disegno date rispettto a x0 e y0
 
 * a e b sono le lunghezze degli ipotenusa che hanno cateti xabs e yabs.
 * D è la distanza tra i vertici superiori (i due supporti del filo)
 * 
 *      ------->x
 *      0----------------------------------D
 *       \      |                       -
 *        \     |                    -
 *         \    |                 -
 *        a \   |             - b
 *           \  | y       -
 *            \ v    -
 *             \-
 * 
 *  a = sqrt(xabs^2 + yabs^2)
 *  b = sqrt(yabs^2 + (D-xabs)^2)
 */
#define x0      401.0
#define y0      500.0
#define D       802.0


 
 
// l'unita' di misura di x e y sono mm
// per passare da mm a passi dell'encoder definiamo mm2pp
// il numero indica quanti passi di motore vengono fatti per spostare il filo di un mm
#define mm2pp   14.222



     
void setup() {
    // initialize serial:
    Serial.begin(9600);
    
    Serial.println("Init");
    Serial.print("mode: ");
    Serial.println(mode);

	myservo.attach(SERVO_PIN);  // attaches the servo pin to the servo object 
	
	penPositioning(PEN_UP);		// alza la penna
	delay (2000); 				// wait servo get its position
	
    // Sets the two pins as Outputs
    pinMode(stepPinA, OUTPUT); 
    pinMode(stepPinB, OUTPUT); 
    pinMode( dirPinA, OUTPUT);
    pinMode( dirPinB, OUTPUT);

	
	// calcola le lunghezze iniziali delle funi
    act_a = sqrt(x0*x0 + y0*y0)*mm2pp;
    act_b = act_a;

    Serial.print(act_a);
    Serial.print(',');
    Serial.println(act_b);


	Serial.print("Initializing SD card...");

	if (!SD.begin(SD_CS)) {
		Serial.println("initialization failed!");
		return;
	}
	Serial.println("initialization done.");


	// open the file. note that only one file can be open at a time,
	// so you have to close this one before opening another.
	dataFile = SD.open(NOME_FILE, FILE_WRITE);


	dataFile = SD.open(NOME_FILE);
	if (!dataFile) {
		// if the file didn't open, print an error:
		Serial.println("error opening xy.txt");
		while(1);
	}	

    Serial.println("done!");


// definisco un insieme di punti a scopo di test	
float xe = 100;
float ye = 150;

    points[0].x = xe;
    points[0].y = ye;
    
    points[1].x =  xe;
    points[1].y = -ye;
    
    points[2].x = -xe;
    points[2].y = -ye;
    
    points[3].x = -xe;
    points[3].y =  ye;
    
    points[4].x =  xe;
    points[4].y =  ye;
    
    points[5].x =  xe;
    points[5].y =   0;
    
    points[6].x =  -xe;
    points[6].y =  0;
    
    points[7].x =  0;
    points[7].y =  0;
    
    points[8].x =  0;
    points[8].y =  -ye;
    
    points[9].x =  0;
    points[9].y =  ye;
    
    points[10].x =  xe;
    points[10].y =  ye;
    
}

void loop() {
int i;
/*
	a scopo di debug è possibilie operare in modi diversi
*/
	// leggo dati da file 
    if (mode == FILE){
        Serial.println("start file mode");
        
        while (readLine()==0){
        	i++;
        	Serial.println(i);
        	Serial.print(x);
        	Serial.print(", ");
        	Serial.println(y);
        	
        	penPositioning(pen);
        	
        	lineAbsUM(x, y);
            delay(10);
        }
        
        penPositioning(PEN_UP);
        Serial.println("drawing done!");
    }	
	
	
//	prendo i dati da un array
    if (mode == ARRAY){
        Serial.println("start array mode");
    	while (1);
        for(i = 0; i <=10; i++){ 
            lineAbsUM(points[i].x, points[i].y);
            delay(1000);
        }
    }
    
// test penna
// serve a trovare le posizioni di penna su e penna giù
// da seriale si invia un valore e questo viene messo in atto
//

    if (mode == TEST_PENNA){
        Serial.println("start test penna mode");
        while(1){
            while (Serial.available() > 0) {
        	x = Serial.parseInt();
                if (Serial.read() == '\n') {
                    Serial.println(x);
                myservo.writeMicroseconds(x);  // tell servo to go to position in variable 'pos' 
        		}
        	}
        }
    }
	

	
// test movimento
// serve a verificare i movimenti e le posizioni raggiunte
// da seriale si invia una coppia x, y separate con una virgola in mm (esempio -100, 20) 
// il plotter si posizionerà di conseguenza.
// 0,0 è il punto di partenza in mezzo al foglio
    if (mode == TEST_XY){
        Serial.println("start test xy mode");
        while(1){
            while (Serial.available() > 0) {
        
                // format x, y
                // look for the next valid integer in the incoming serial stream:
                x = Serial.parseInt();
                // do it again:
                y = Serial.parseInt();
                
                // look for the newline. That's the end of your
                // sentence:
                if (Serial.read() == '\n') {
                    // constrain the values to -50 - 50
//                    x = constrain(x, -150, 150);
//                    y = constrain(y, -200, 200);
            
                    Serial.print(x);
                    Serial.print(',');
                    Serial.println(y);
                    lineAbsUM(x,y);
                    delay(1000);
                }    
            }
        }    
    }    
}

/*
 * si muove linearmente da pos attuale a x, y
 */ 
void lineAbsUM(float x, float y){
float af, bf;
long int    ai, bi;
	// trova x e y assoluti
    x  = x + x0;
    y  = y + y0;
    
	// determina af e bf (valori assoluti degli assi)
    af = sqrt(x*x + y*y);
    bf = sqrt(y*y + (D - x)*(D - x));
    Serial.print("a, b: ");
    Serial.print(af);
    Serial.print(',');
    Serial.println(bf);

	// assi in impulsi
    ai = af*mm2pp;
    bi = bf*mm2pp;
    Serial.print(ai);
    Serial.print(',');
    Serial.println(bi);

    Serial.print("actual a, b: ");
    Serial.print(act_a);
    Serial.print(',');
    Serial.println(act_b);
    
    line(ai, bi);
    Serial.print("end a, b: ");
    Serial.print(act_a);
    Serial.print(',');
    Serial.println(act_b);
}

// movimento a posizione assoluta
// prima move un asse poi muove l'altro
void moveAbs(long int a, long int b){

long int stepa, stepb;


    if (a > act_a){
        stepa =  1;
        digitalWrite(dirPinA, LOW); // rotations direction
    }
    else{
        stepa = -1;
        digitalWrite(dirPinA,  HIGH); // rotations direction
    }

    while (act_a != a){
        digitalWrite(stepPinA,HIGH);
        delayMicroseconds(1500);
        digitalWrite(stepPinA,LOW);
        delayMicroseconds(1500);
        act_a += stepa;
    }

    if (b > act_b){
        stepb =  1;
        digitalWrite(dirPinB, LOW); // rotations direction
    }
    else{
        stepb = -1;
        digitalWrite(dirPinB,  HIGH); // rotations direction
    }

    while (act_b != b){
        digitalWrite(stepPinB,HIGH);
        delayMicroseconds(1500);
        digitalWrite(stepPinB,LOW);
        delayMicroseconds(1500);
        act_b += stepb;
    }
}

/*
 * si muove linearmente da pos attuale a x, y
 * http://www.marginallyclever.com/2013/08/27/how-to-build-an-2-axis-arduino-cnc-gcode-interpreter/
 */ 
void line(long int a,long int b) {
long int da = a - act_a; // distance to move (delta)
long int db = b - act_b;
long int stepa, stepb;


    if (a > act_a){
        stepa =  1;
        digitalWrite(dirPinA, LOW); // rotations direction
    }
    else{
        stepa = -1;
        digitalWrite(dirPinA,  HIGH); // rotations direction
    }

    if (b > act_b){
        stepb =  1;
        digitalWrite(dirPinB, LOW); // rotations direction
    }
    else{
        stepb = -1;
        digitalWrite(dirPinB,  HIGH); // rotations direction
    }


    da=abs(da); // absolute delta
    db=abs(db);

long int i;
long int over=0;

    if(da>db) {
        for(i=0;i<da;++i) {
//            m1.onestep(dirx);
            digitalWrite(stepPinA,HIGH);
            delayMicroseconds(PDURATION);
            digitalWrite(stepPinA,LOW);
            delayMicroseconds(PDURATION);
            act_a += stepa;

            over +=db;
            if(over>=da) {
                over -=da;
    //            m2.onestep(diry);
                digitalWrite(stepPinB,HIGH);
                delayMicroseconds(PDURATION);
                digitalWrite(stepPinB,LOW);
                delayMicroseconds(PDURATION);
                act_b += stepb;
            }
        }
    }
    else {
        for(i=0;i<db;++i) {
//            m1.onestep(dirx);
            digitalWrite(stepPinB,HIGH);
            delayMicroseconds(PDURATION);
            digitalWrite(stepPinB,LOW);
            delayMicroseconds(PDURATION);
            act_b += stepb;

            over +=da;
            if(over>=db) {
                over -=db;
                digitalWrite(stepPinA,HIGH);
                delayMicroseconds(PDURATION);
                digitalWrite(stepPinA,LOW);
                delayMicroseconds(PDURATION);
                act_a += stepa;
            }// 
        }
    }
}

/*
 legge una riga per volta dal file
 mette i valori su x, y e pen
 ritorna -1 in caso di errore 
*/
int readLine(void){

#define MAX_STRING_LEN 64
char inStr[MAX_STRING_LEN];
bool 	validStr;
int 	i = 0;
char 	c;
const char s[2] = ";";
char *token;

float var;
float input[3];

	validStr = false;

	if (dataFile.available()){
		//read characters until we find a new line, hit end of file, 
		//or run out of room in our string buffer.
		do{
			c = dataFile.read();
			inStr[i++] = c;
		}
		while ((c != '\n') && (i < MAX_STRING_LEN) && (dataFile.available()));
		inStr[i] = 0; // string terminator
		validStr = (c == '\n');   //input string is valid if we read a new line
		//if string is not valid, keep reading until we find a new line 
		//or run into the end of the file
		if (!validStr){
			while ((c != '\n') && (dataFile.available())){
			c = dataFile.read();
			}
		}
//		Serial.println(inStr);

		/* get the first token */
		token = strtok(inStr, s);
//		Serial.println(inStr);
		/* walk through other tokens */
		i = 0;
		while( token != NULL ) {
			var = atof(token);
//			Serial.println(token);
			input[i++] = var;
//			Serial.println(var);
			token = strtok(NULL, s);
		}
		x   = input[0];
		y   = input[1];
		pen = input[2];
		return(0);
	}
	return(-1);
}

// posiziona il servo che muove la penna
void penPositioning(int penState){
static int pos = PEN_DW;    // variable to store the servo position 
static int posRef;  		// variable to store the servo position reference	

	if (penState)	posRef = PEN_DW;
	else			posRef = PEN_UP;

	if( posRef == pos ) return;
	
	while (posRef != pos){
		if (posRef > pos)   pos++;
		if (posRef < pos)   pos--;
//		myservo.write(pos);              // tell servo to go to position in variable 'pos' 
        myservo.writeMicroseconds(pos);  // tell servo to go to position in variable 'pos' 

        delay(15);                       // waits 15ms for the servo to reach the position 
	}
	delay(1000); 		// stabilizzazione
}
