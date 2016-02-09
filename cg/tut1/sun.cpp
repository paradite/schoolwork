//
//  main.cpp
//  tut2
//
//  Created by Zhu Liang on 24/1/16.
//  Copyright (c) 2016 Zhu Liang. All rights reserved.

#include <math.h>

#ifdef _WIN32
//define something for Windows (32-bit and 64-bit, this part is common)
#include <GL/glut.h>
#include <GL/glu.h>
#include <GL/gl.h>
#ifdef _WIN64
//define something for Windows (64-bit only)
#endif
#elif __APPLE__
#include <GLUT/glut.h>
#include <OpenGL/gl.h>
#include <OpenGL/glu.h>
#elif __linux__
// linux
#elif __unix__ // all unices not caught above
// Unix
#elif defined(_POSIX_VERSION)
// POSIX
#else
#   error "Unknown compiler"
#endif

const float DEG2RAD = 3.14159/180;

void drawAUnitSquare(){
    glBegin(GL_POLYGON);
    glVertex3f(-1.0, -1.0, 0.0);
    glVertex3f(-1.0, 1.0, 0.0);
    glVertex3f(1.0, 1.0, 0.0);
    glVertex3f(1.0, -1.0, 0.0);
    glEnd();
}

void drawSquaresRecur(int n){
    if (n==0) return;
    glTranslatef(0,1.85,0);
    glRotatef(15,0,0,1);
    glScalef(0.55,0.55,0.55);
    drawAUnitSquare();
    drawSquaresRecur(n-1);
}

void drawSquares(int n){
    // Initial scale and position
    //    glTranslatef(0,-0.75,0);
    glScalef(0.25,0.25,0.25);
    drawAUnitSquare();
    drawSquaresRecur(n);
}

void drawSun(){
    for (int i = 0; i < 8; i++) {
        glPushMatrix();
        glRotatef(360/8*i,0,0,1);
        drawSquares(7);
        glPopMatrix();
    }
}

void mydisplay(){
    glClearColor(1.0,1.0,1.0,1.0);
    glClear(GL_COLOR_BUFFER_BIT);
    
    glColor3f(1.0,0.0,0.0);
    glLoadIdentity();
    drawSun();
    glFlush();
}

int main(int argc, char **argv) {
    glutInit(&argc, argv);
    glutCreateWindow("CS3241 Tutorial 2");
    glutDisplayFunc(mydisplay);
    glutMainLoop();
}







