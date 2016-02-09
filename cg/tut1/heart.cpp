//
//  main.cpp
//  CS3241 Tutorial 1
//
//  Created by Zhu Liang on 15/1/16.
//  Copyright (c) 2016 Zhu Liang. All rights reserved.
//

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

void drawCircle(float radius){
    glBegin(GL_LINE_LOOP);
//    glBegin(GL_TRIANGLE_FAN);
    
    for (int i=0; i < 359; i++)
    {
        float degInRad = i*DEG2RAD;
        glVertex2f(cos(degInRad)*radius,sin(degInRad)*radius);
    }
    
    glEnd();
}

void drawSpiral(){
    float radius = 0.1;
    glBegin(GL_LINE_STRIP);
    //    glBegin(GL_TRIANGLE_FAN);
    
//    for (int i=90; i > -270; i--){
    for (int i=90; i > -91; i--){
        radius = radius + 0.0025;
        float degInRad = i * DEG2RAD;
        glVertex2f(cos(degInRad)*radius,sin(degInRad)*radius);
    }
    
    glEnd();
}

void drawDoubleSpiral(){
    glLoadIdentity();
    drawSpiral();
    // Reflection by scaling
    glScalef(-1, 1, 1);
    drawSpiral();
}

void mydisplay(){
    glClearColor(1.0,1.0,1.0,1.0);
    glClear(GL_COLOR_BUFFER_BIT);
    
    glColor3f(1.0,0.0,0.0);
    glLoadIdentity();
//    drawSun();
    drawDoubleSpiral();
    glFlush();
}

int main(int argc, char **argv) {
    glutInit(&argc, argv);
    glutCreateWindow("CS3241 Tutorial 1");
    glutDisplayFunc(mydisplay);
    glutMainLoop();
}







