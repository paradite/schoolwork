// CS3241Lab1.cpp : Defines the entry point for the console application.
#include <cmath>
#include <iostream>

/* Include header files depending on platform */
#ifdef _WIN32
    #include "glut.h"
    #define M_PI 3.14159
#elif __APPLE__
    #include <OpenGL/gl.h>
    #include <GLUT/GLUT.h>
#endif

using namespace std;

float alpha = 0.0, k=1;
float tx = 0.0, ty=0.0;

const float DEG2RAD = 3.14159/180;

// Android drawing parameters

// Shift body down by 2 unit;
float bodyShift = -2;
float bodyLength = 10.0;

float headRadius = 5.0;
float antennaWidth = 0.3;
float antennaHeight = 6.0;
float antennaAngle = 35.0;
float antennaShiftX = 2.0;
float antennaShiftY = 3.0;

float armLength = 6.0;
float armWidth = 1.5;
float handRadius = armWidth / 2;

float defaultGap = 0.5;


void drawFullCircle(float radius){
    // glBegin(GL_LINE_STRIP);
    glBegin(GL_POLYGON);
    
    for (int i=0; i < 360; i++)
    {
        float degInRad = i*DEG2RAD;
        glVertex2f(cos(degInRad)*radius,sin(degInRad)*radius);
    }
    
    glEnd();
}

void drawHalfCircle(float radius){
    // glBegin(GL_LINE_STRIP);
    glBegin(GL_POLYGON);
    
    for (int i=0; i < 181; i++)
    {
        float degInRad = i*DEG2RAD;
        glVertex2f(cos(degInRad)*radius,sin(degInRad)*radius);
    }
    
    glEnd();
}

void drawFullRect(float x, float y){
    glBegin(GL_POLYGON);
        glVertex2f(-x/2 , -y/2);
        glVertex2f(-x/2 , y/2);
        glVertex2f(x/2 , y/2);
        glVertex2f(x/2 , -y/2);
    glEnd();
}

void drawFullSquare(float length) {
    drawFullRect(length, length);
}

void drawAntenna(){
    drawFullRect(antennaWidth, antennaHeight);
    glTranslatef(0, antennaHeight/2, 0);
    drawFullCircle(antennaWidth/2);
}

void drawEye(){
    glColor3f(1.0, 1.0, 1.0);
    drawFullCircle(headRadius/12);
    glColor3f(0.643, 0.792, 0.224);
}

void drawHead() {
    glPushMatrix();
        glTranslatef(0, bodyLength /2 + bodyShift + defaultGap, 0);
        drawHalfCircle(headRadius);
        glPushMatrix();
            glTranslatef(-headRadius/2.2, headRadius/2.2,0);
            drawEye();  
        glPopMatrix();
        glPushMatrix();
            glTranslatef(headRadius/2.2, headRadius/2.2,0);
            drawEye();  
        glPopMatrix();
        glPushMatrix();
            glTranslatef(-antennaShiftX, antennaShiftY, 0);
            glRotatef(antennaAngle, 0, 0, 1);
            drawAntenna();
        glPopMatrix();
        glPushMatrix();
            glTranslatef(antennaShiftX, antennaShiftY, 0);
            glRotatef(-antennaAngle, 0, 0, 1);
            drawAntenna();
        glPopMatrix();
    glPopMatrix();
}

void drawBody(){
    glPushMatrix();
        glTranslatef(0, bodyShift, 0);
        drawFullSquare(bodyLength);
    glPopMatrix();
}

void drawHand(){
    glPushMatrix();
        drawHalfCircle(handRadius);
    glPopMatrix();
}

void drawArms(){
    // Left arm
    glPushMatrix();
    glTranslatef(-bodyLength/2 - armWidth/2 - defaultGap, bodyShift + (bodyLength - armLength)/2 - handRadius/2, 0);
    drawFullRect(armWidth, armLength);
    glTranslatef(0, (armLength)/2, 0);
    drawHand();
    glPopMatrix();
    // Right arm
    glPushMatrix();
    glTranslatef(bodyLength/2 + armWidth/2 + defaultGap, bodyShift + (bodyLength - armLength)/2 - handRadius/2, 0);
    drawFullRect(armWidth, armLength);
    glTranslatef(0, (armLength)/2, 0);
    drawHand();
    glPopMatrix();
}

void display(void)
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    glPushMatrix();

    //controls transformation
    glScalef(k, k, k);
    glTranslatef(tx, ty, 0);
    glRotatef(alpha, 0, 0, 1);
    
    //draw your stuff here
    // Android color
    glColor3f(0.643, 0.792, 0.224);
    glTranslatef(5, -5, 0);
    glRotatef(45, 0, 0, 1);
    glScalef(1.5, 1.5, 1);
    drawHead();
    drawBody();
    drawArms();
    glPopMatrix();
    glFlush ();
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
    glClearColor (1.0, 1.0, 1.0, 1.0);
    glShadeModel (GL_SMOOTH);
}



void keyboard (unsigned char key, int x, int y)
{
    //keys to control scaling - k
    //keys to control rotation - alpha
    //keys to control translation - tx, ty
    switch (key) {

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
    cout<<"CS3241 Lab 1\n\n";
    cout<<"+++++CONTROL BUTTONS+++++++\n\n";
    cout<<"Scale Up/Down: Q/E\n";
    cout<<"Rotate Clockwise/Counter-clockwise: A/D\n";
    cout<<"Move Up/Down: W/S\n";
    cout<<"Move Left/Right: Z/C\n";
    cout <<"ESC: Quit\n";

    glutInit(&argc, argv);
    glutInitDisplayMode (GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE);
    glutInitWindowSize (600, 600);
    glutInitWindowPosition (50, 50);
    glutCreateWindow (argv[0]);
    init ();
    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    //glutMouseFunc(mouse);
    glutKeyboardFunc(keyboard);
    glutMainLoop();

    return 0;
}
