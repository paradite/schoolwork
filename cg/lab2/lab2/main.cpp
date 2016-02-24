// CS3241Lab2.cpp : Defines the entry point for the console application.
#include <cmath>
#include <iostream>
#include <chrono>
/* Include header files depending on platform */
#ifdef _WIN32
    #include <time.h>
	#include "glut.h"
	#define M_PI 3.14159
#elif __APPLE__
	#include <OpenGL/gl.h>
	#include <GLUT/GLUT.h>
#endif

using namespace std;
using namespace std::chrono;

#define numStars 100
#define numPlanets 9

class planet
{
public:
	float distFromRef;
	float angularSpeed;
	GLfloat color[3];
	float size;
	float angle;
    int roleInClock; // -1: fade away, 0: normal, 1: second, 2: minute, 3: hour

	planet()
	{
		distFromRef = 0;
		angularSpeed = 0;
		color[0] = color[1] = color[2] = 0;
		size = 0;
		angle = 0;
        roleInClock = -1;
	}
    
    planet(float args[]) {
        distFromRef = args[0];
        angularSpeed = args[1];
        color[0] = args[2];
        color[1] = args[3];
        color[2] = args[4];
        size = args[5];
        angle = args[6];
        roleInClock = -1;
    }
};

float alpha = 0.0, k=1;
float tx = 0.0, ty=0.0;
planet planetList[numPlanets];

const float DEG2RAD = 3.14159/180;
const float SHADE_FACTOR = 0.6;
bool clockMode = false;

void switchMode(){
    clockMode = !clockMode;
}

void drawFullCircleWithShade(float radius, GLfloat color[], float transparency){
    glColor4f(color[0], color[1], color[2], transparency);
//    glBegin(GL_LINE_STRIP);
    glBegin(GL_POLYGON);
    
    for (int i=-90; i < 270; i++){
        if(i > -90 && i <= 90){
            glColor4f(color[0] * SHADE_FACTOR, color[1] * SHADE_FACTOR, color[2] * SHADE_FACTOR, transparency);
        } else {
            glColor4f(color[0], color[1], color[2], transparency);
        }
        float degInRad = i*DEG2RAD;
        glVertex2f(cos(degInRad)*radius,sin(degInRad)*radius);
    }
    
    glEnd();
}


void drawFullCircle(float radius, GLfloat color[], float transparency){
    glColor4f(color[0], color[1], color[2], transparency);
    // glBegin(GL_LINE_STRIP);
    glBegin(GL_POLYGON);
    
    for (int i=0; i < 360; i++)
    {
        float degInRad = i*DEG2RAD;
        glVertex2f(cos(degInRad)*radius,sin(degInRad)*radius);
    }
    
    glEnd();
}

void initPlanets(){
    // colors from https://github.com/ajstarks/openvg/blob/master/go-client/planets/planets.go
    float planetArgs[numPlanets][7] = {
        {0, 0, 247/255.0, 115/255.0, 12/255.0, 2, 0}, // sun
        {1, 2, 250/255.0, 248/255.0, 242/255.0, 0.38, 40}, // mercury
        {2, 4, 255.0/255.0, 255.0/255.0, 242/255.0, 0.95, 10}, // venus
        {3, 10, 11/255.0, 92/255.0, 227/255.0, 1.0, 70}, // earth
        {4, 4, 240/255.0, 198/255.0, 29/255.0, 0.53, 100}, // mars
        {5, 1, 253/255.0, 199/255.0, 145/255.0, 2.0, 130}, // jupiter
        {6.0, 7, 224/255.0, 196/255.0, 34/255.0, 1.9, 190}, // saturn
        {7.2, 12, 220/255.0, 241/255.0, 245/255.0, 1.4, 200}, // uranus
        {8, 3, 57/255.0, 182/255.0, 247/255.0, 1.3, 230}, // neptune
    };
    
    int rolesInClock[numPlanets] = {0, 1, -1, 2, -1, 3, -1, -1, -1};
    for (int i = 0; i < numPlanets; i++) {
        planetList[i] = planet(planetArgs[i]);
        planetList[i].roleInClock = rolesInClock[i];
    }
}

void drawPlanet(planet p, float clockAngleMilli){
    glPushMatrix();
    float finalAngle = clockAngleMilli * p.angularSpeed + p.angle;
    finalAngle = fmod(finalAngle, 360.0);
    float degInRad = finalAngle * DEG2RAD;
    glTranslatef(cos(degInRad) * p.distFromRef, sin(degInRad) * p.distFromRef, 1);
    glRotatef(finalAngle, 0, 0, 1);
    if(p.distFromRef == 0){
        // no shade for sun
        drawFullCircle(p.size/3, p.color, 1);
    } else {
        drawFullCircleWithShade(p.size/3, p.color, 1);
    }
    glPopMatrix();
}

void drawPlanetInClockMode(planet p, float clockAngleHour, float clockAngleMin, float clockAngleSec, float clockAngleMilli){
    glPushMatrix();
    float finalAngle = 0;
    float transparency = 1;
    if(p.roleInClock == -1){
        finalAngle = clockAngleMilli * p.angularSpeed + p.angle;
        transparency = 0.2;
    } else if(p.roleInClock == 0){
        finalAngle = 0;
    } else if(p.roleInClock == 1){
        finalAngle = clockAngleSec;
    } else if(p.roleInClock == 2){
        finalAngle = clockAngleMin;
    } else if(p.roleInClock == 3){
        finalAngle = clockAngleHour;
    }
    float degInRad = finalAngle * DEG2RAD;
    glTranslatef(cos(degInRad) * p.distFromRef, sin(degInRad) * p.distFromRef, 1);
    glRotatef(finalAngle, 0, 0, 1);
    drawFullCircleWithShade(p.size/3, p.color, transparency);
    glPopMatrix();
}

void drawPlanets() {
    glPushMatrix();
    
    milliseconds ms = duration_cast< milliseconds >(system_clock::now().time_since_epoch());
    int milli = ms.count()%(60000);
    double angleMilli = 360 - (float)milli/60000 * 360;
    
    if(clockMode) {
        time_t current_time = time (NULL);
        
        struct tm * timeinfo = localtime(&current_time);
        double angleSec = 360-(float)timeinfo->tm_sec/60*360 + 90;
        double angleMin = 360-(float)timeinfo->tm_min/60*360 + 90;
        double angleHour = 360-(float)timeinfo->tm_hour/24*360 + 90;
        
//        printf("%i %i %i\n", timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec);
//        printf("%f %f %f\n", angleHour, angleMin, angleSec);
        
        for (int i = 0; i < numPlanets; i++) {
            drawPlanetInClockMode(planetList[i], angleHour, angleMin, angleSec, angleMilli);
        }
        
    } else {
        
        //    printf("%i\n", milli);
        
        for (int i = 0; i < numPlanets; i++) {
            drawPlanet(planetList[i], angleMilli);
        }
    }
    glPopMatrix();
}

void reshape (int w, int h)
{
	glViewport (0, 0, (GLsizei) w, (GLsizei) h);

	glMatrixMode (GL_PROJECTION);
	glLoadIdentity();

	glOrtho(-10, 10, -10, 10, -10, 10);
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity();
}

void init(void)
{
	glClearColor (0.0, 0.0, 0.3, 1.0);
	glShadeModel (GL_SMOOTH);
	glEnable(GL_BLEND);
	glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
}

void display(void)
{
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	
	glPushMatrix();

	//controls transformation
	glScalef(k, k, k);	
	glTranslatef(tx, ty, 0);	
	glRotatef(alpha, 0, 0, 1);

    initPlanets();
	drawPlanets();

	glPopMatrix();
	glFlush ();
}

void idle()
{
	//update animation here
	
	glutPostRedisplay();	//after updating, draw the screen again
}

void keyboard (unsigned char key, int x, int y)
{
	//keys to control scaling - k
	//keys to control rotation - alpha
	//keys to control translation - tx, ty
	switch (key) {

        case 't':
            switchMode();
        break;
            
		case 'a':
			alpha+=10;
			glutPostRedisplay();
		break;

		case 'd':
			alpha-=10;
			glutPostRedisplay();
		break;

		case 'q':
			k+=0.1;
			glutPostRedisplay();
		break;

		case 'e':
			if(k>0.1)
				k-=0.1;
			glutPostRedisplay();
		break;

		case 'z':
			tx-=0.1;
			glutPostRedisplay();
		break;

		case 'c':
			tx+=0.1;
			glutPostRedisplay();
		break;

		case 's':
			ty-=0.1;
			glutPostRedisplay();
		break;

		case 'w':
			ty+=0.1;
			glutPostRedisplay();
		break;
		
		case 27:
			exit(0);
		break;

		default:
		break;
	}
}

int main(int argc, char **argv)
{
	cout<<"CS3241 Lab 2\n\n";
	cout<<"+++++CONTROL BUTTONS+++++++\n\n";
	cout<<"Scale Up/Down: Q/E\n";
	cout<<"Rotate Clockwise/Counter-clockwise: A/D\n";
	cout<<"Move Up/Down: W/S\n";
	cout<<"Move Left/Right: Z/C\n";
	cout <<"ESC: Quit\n";

	glutInit(&argc, argv);
	glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE); // anti aliasing
	glutInitWindowSize (600, 600);
	glutInitWindowPosition (50, 50);
	glutCreateWindow (argv[0]);
	init ();
	glutDisplayFunc(display);
	glutIdleFunc(idle);
	glutReshapeFunc(reshape);	
	//glutMouseFunc(mouse);
	glutKeyboardFunc(keyboard);
	glutMainLoop();

	return 0;
}
