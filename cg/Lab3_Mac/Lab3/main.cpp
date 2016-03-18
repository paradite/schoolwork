// CS3241Lab3.cpp : Defines the entry point for the console application.
//#include <cmath>
#include "math.h"
#include <iostream>
#include <fstream>

#ifdef _WIN32
	#include <Windows.h>
	#include "glut.h"
	#define M_PI 3.141592654
#elif __APPLE__
	#include <OpenGL/gl.h>
	#include <GLUT/GLUT.h>
#endif

// global variable

bool m_Smooth = false;
bool m_Highlight = false;
GLfloat angle = 0;   /* in degrees */
GLfloat angle2 = 0;   /* in degrees */
GLfloat zoom = 1.0;
int mouseButton = 0;
int moving, startx, starty;

#define NO_OBJECT 4;
int current_object = 0;

using namespace std;

float no_mat[] = {0.0f, 0.0f, 0.0f, 1.0f};
float mat_ambient[] = {0.3f, 0.3f, 0.3f, 1.0f};

// Blue color texture
float mat_diffuse_blue[] = {0.1f, 0.5f, 0.8f, 1.0f};
float mat_emission_blue[] = {0.025f, 0.125f, 0.2f, 0.0f};
float mat_highlight_blue[] = { 0.4f, 0.8f, 1.1f, 1.0f };

// Silver color texture
float mat_diffuse_silver[] = {0.75f, 0.75f, 0.75f, 1.0f};
float mat_emission_silver[] = {0.1f, 0.1f, 0.1f, 0.0f};
float mat_highlight_silver[] = { 0.3f, 0.3f, 0.3f, 1.0f };

// small particle parameters
const int SMALL_PARTICLES_NUMBER = 50;
float small_particle_params[SMALL_PARTICLES_NUMBER][4];

void setupLighting()
{
	glShadeModel(GL_SMOOTH);
	glEnable(GL_NORMALIZE);

	// Lights, material properties
    GLfloat	ambientProperties[]  = {0.7f, 0.7f, 0.7f, 1.0f};
	GLfloat	diffuseProperties[]  = {0.8f, 0.8f, 0.8f, 1.0f};
    GLfloat	specularProperties[] = {1.0f, 1.0f, 1.0f, 1.0f};
	GLfloat lightPosition[] = {-100.0f,100.0f,100.0f,1.0f};
	
    glClearDepth( 1.0 );

    glLightfv( GL_LIGHT0, GL_AMBIENT, ambientProperties);
    glLightfv( GL_LIGHT0, GL_DIFFUSE, diffuseProperties);
	glLightfv( GL_LIGHT0, GL_SPECULAR, specularProperties);
	glLightfv( GL_LIGHT0, GL_POSITION, lightPosition);
	
    glLightModelf(GL_LIGHT_MODEL_TWO_SIDE, 0.0);

	// Default : lighting
	glEnable(GL_LIGHT0);
	glEnable(GL_LIGHTING);

}


void drawSphere(double r, float mat_diffuse[], float mat_emission[], float mat_highlight[])
{
	float no_shininess = 0.0f;
	float shininess = 80.0f;
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient);
	glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse);
	glMaterialfv(GL_FRONT, GL_EMISSION, mat_emission);

	if(m_Highlight)
	{
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_highlight);
        glMaterialf(GL_FRONT, GL_SHININESS, shininess);
	} else {
		glMaterialfv(GL_FRONT, GL_SPECULAR, no_mat);
		glMaterialf(GL_FRONT, GL_SHININESS, no_shininess);
	}

	
    int i,j;
	int n = 40;
    for(i=0;i<n;i++)
		for(j=0;j<2*n;j++)
		if(m_Smooth)
		{
			glBegin(GL_POLYGON);
			    // the normal of each vertex is actaully its own coordinates normalized for a sphere
                glNormal3d(sin(i*M_PI/n)*cos(j*M_PI/n),cos(i*M_PI/n)*cos(j*M_PI/n),sin(j*M_PI/n));
                glVertex3d(r*sin(i*M_PI/n)*cos(j*M_PI/n),r*cos(i*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
			    glNormal3d(sin((i+1)*M_PI/n)*cos(j*M_PI/n),cos((i+1)*M_PI/n)*cos(j*M_PI/n),sin(j*M_PI/n));
				glVertex3d(r*sin((i+1)*M_PI/n)*cos(j*M_PI/n),r*cos((i+1)*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
			    glNormal3d(sin((i+1)*M_PI/n)*cos((j+1)*M_PI/n),cos((i+1)*M_PI/n)*cos((j+1)*M_PI/n),sin((j+1)*M_PI/n));
				glVertex3d(r*sin((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*cos((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
			    glNormal3d(sin(i*M_PI/n)*cos((j+1)*M_PI/n),cos(i*M_PI/n)*cos((j+1)*M_PI/n),sin((j+1)*M_PI/n));
				glVertex3d(r*sin(i*M_PI/n)*cos((j+1)*M_PI/n),r*cos(i*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
 			glEnd();
		} else	{
			glBegin(GL_POLYGON);
			    // Explanation: the normal of the whole polygon is the coordinate of the center of the polygon for a sphere
			    glNormal3d(sin((i+0.5)*M_PI/n)*cos((j+0.5)*M_PI/n),cos((i+0.5)*M_PI/n)*cos((j+0.5)*M_PI/n),sin((j+0.5)*M_PI/n));
				glVertex3d(r*sin(i*M_PI/n)*cos(j*M_PI/n),r*cos(i*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
				glVertex3d(r*sin((i+1)*M_PI/n)*cos(j*M_PI/n),r*cos((i+1)*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
				glVertex3d(r*sin((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*cos((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
				glVertex3d(r*sin(i*M_PI/n)*cos((j+1)*M_PI/n),r*cos(i*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
 			glEnd();
		}

}

void drawHalfSphere(double r, float mat_diffuse[], float mat_emission[], float mat_highlight[])
{
    float no_shininess = 0.0f;
    float shininess = 80.0f;
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient);
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse);
    glMaterialfv(GL_FRONT, GL_EMISSION, mat_emission);
    
    if(m_Highlight)
    {
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_highlight);
        glMaterialf(GL_FRONT, GL_SHININESS, shininess);
    } else {
        glMaterialfv(GL_FRONT, GL_SPECULAR, no_mat);
        glMaterialf(GL_FRONT, GL_SHININESS, no_shininess);
    }
    
    
    int i,j;
    int n = 40;
    for(i=0;i<n;i++)
        for(j=0;j<n;j++)
            if(m_Smooth)
            {
                glBegin(GL_POLYGON);
                // the normal of each vertex is actaully its own coordinates normalized for a sphere
                glNormal3d(sin(i*M_PI/n)*cos(j*M_PI/n),cos(i*M_PI/n)*cos(j*M_PI/n),sin(j*M_PI/n));
                glVertex3d(r*sin(i*M_PI/n)*cos(j*M_PI/n),r*cos(i*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
                glNormal3d(sin((i+1)*M_PI/n)*cos(j*M_PI/n),cos((i+1)*M_PI/n)*cos(j*M_PI/n),sin(j*M_PI/n));
                glVertex3d(r*sin((i+1)*M_PI/n)*cos(j*M_PI/n),r*cos((i+1)*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
                glNormal3d(sin((i+1)*M_PI/n)*cos((j+1)*M_PI/n),cos((i+1)*M_PI/n)*cos((j+1)*M_PI/n),sin((j+1)*M_PI/n));
                glVertex3d(r*sin((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*cos((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
                glNormal3d(sin(i*M_PI/n)*cos((j+1)*M_PI/n),cos(i*M_PI/n)*cos((j+1)*M_PI/n),sin((j+1)*M_PI/n));
                glVertex3d(r*sin(i*M_PI/n)*cos((j+1)*M_PI/n),r*cos(i*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
                glEnd();
            } else	{
                glBegin(GL_POLYGON);
                // Explanation: the normal of the whole polygon is the coordinate of the center of the polygon for a sphere
                glNormal3d(sin((i+0.5)*M_PI/n)*cos((j+0.5)*M_PI/n),cos((i+0.5)*M_PI/n)*cos((j+0.5)*M_PI/n),sin((j+0.5)*M_PI/n));
                glVertex3d(r*sin(i*M_PI/n)*cos(j*M_PI/n),r*cos(i*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
                glVertex3d(r*sin((i+1)*M_PI/n)*cos(j*M_PI/n),r*cos((i+1)*M_PI/n)*cos(j*M_PI/n),r*sin(j*M_PI/n));
                glVertex3d(r*sin((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*cos((i+1)*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
                glVertex3d(r*sin(i*M_PI/n)*cos((j+1)*M_PI/n),r*cos(i*M_PI/n)*cos((j+1)*M_PI/n),r*sin((j+1)*M_PI/n));
                glEnd();
            }
    
}

void drawCylinder(double r, double height, float mat_diffuse[], float mat_emission[], float mat_highlight[]) {
    glPushMatrix();
    glRotatef(90, 0, 1, 0);
    glTranslatef(0, 0, -height/2);
    float no_shininess = 0.0f;
    float shininess = 80.0f;
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient);
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse);
    glMaterialfv(GL_FRONT, GL_EMISSION, mat_emission);
    
    if(m_Highlight)
    {
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_highlight);
        glMaterialf(GL_FRONT, GL_SHININESS, shininess);
    } else {
        glMaterialfv(GL_FRONT, GL_SPECULAR, no_mat);
        glMaterialf(GL_FRONT, GL_SHININESS, no_shininess);
    }
    
    int i,j;
    int n = 80;
    for(i=0;i<n;i++)
        for(j=0;j<n;j++)
            if(m_Smooth)
            {
                glBegin(GL_POLYGON);
                glNormal3d(sin((i)*M_PI/n * 2),cos((i)*M_PI/n * 2),0);
                glVertex3d(r*sin(i*M_PI/n * 2),r*cos(i*M_PI/n * 2),j/(n) * height);
                glNormal3d(sin((i+1)*M_PI/n * 2),cos((i+1)*M_PI/n * 2),0);
                glVertex3d(r*sin((i+1)*M_PI/n * 2),r*cos((i+1)*M_PI/n * 2),j/(n) * height);
                glNormal3d(sin((i+1)*M_PI/n * 2),cos((i+1)*M_PI/n * 2),0);
                glVertex3d(r*sin((i+1)*M_PI/n * 2),r*cos((i+1)*M_PI/n * 2),(j+1)/(n) * height);
                glNormal3d(sin((i)*M_PI/n * 2),cos((i)*M_PI/n * 2),0);
                glVertex3d(r*sin(i*M_PI/n * 2),r*cos(i*M_PI/n * 2),(j+1)/(n) * height);
                glEnd();
            } else	{
                glBegin(GL_POLYGON);
                glNormal3d(sin((i+0.5)*M_PI/n * 2),cos((i+0.5)*M_PI/n * 2),0);
                glVertex3d(r*sin(i*M_PI/n * 2),r*cos(i*M_PI/n * 2),j/(n) * height);
                glVertex3d(r*sin((i+1)*M_PI/n * 2),r*cos((i+1)*M_PI/n * 2),j/(n) * height);
                glVertex3d(r*sin((i+1)*M_PI/n * 2),r*cos((i+1)*M_PI/n * 2),(j+1)/(n) * height);
                glVertex3d(r*sin(i*M_PI/n * 2),r*cos(i*M_PI/n * 2),(j+1)/(n) * height);
                glEnd();
            }
    glPopMatrix();
}

void drawLeftPill() {
    glPushMatrix();
    glRotatef(-90, 0, 1, 0);
    drawHalfSphere(1, mat_diffuse_blue, mat_emission_blue, mat_highlight_blue);
    glPopMatrix();
    glTranslatef(0.5, 0, 0);
    drawCylinder(1, 1, mat_diffuse_blue, mat_emission_blue, mat_highlight_blue);
}

void drawRightPill() {
    drawCylinder(1, 1, mat_diffuse_silver, mat_emission_silver, mat_highlight_silver);
    glTranslatef(0.5, 0, 0);
    glPushMatrix();
    glRotatef(90, 0, 1, 0);
    drawHalfSphere(1, mat_diffuse_silver, mat_emission_silver, mat_highlight_silver);
    glPopMatrix();
}

void drawFullPill() {
    drawLeftPill();
    glTranslatef(1, 0, 0);
    drawRightPill();
}

void generateSmallParticlesParams() {
    unsigned int time_ui = static_cast<unsigned int>(time(NULL));
    srand(time_ui);
    for (int i = 0; i < SMALL_PARTICLES_NUMBER; i++) {
        float color = rand() % 2;
        float x = static_cast <float> (rand()) / (static_cast <float> (RAND_MAX/2.0));
        float y = static_cast <float> (rand()) / (static_cast <float> (RAND_MAX/3.0));
        float z = static_cast <float> (rand()) / (static_cast <float> (RAND_MAX/2.0));
        small_particle_params[i][0] = x;
        small_particle_params[i][1] = y;
        small_particle_params[i][2] = z;
        small_particle_params[i][3] = color;
    }
}

void drawSmallSpheres() {
    glPushMatrix();
    glTranslatef(-1.0, -2.5, 0);
    for (int i = 0; i < SMALL_PARTICLES_NUMBER; i++) {
        glPushMatrix();
        float x = small_particle_params[i][0];
        float y = small_particle_params[i][1];
        float z = small_particle_params[i][2];
        float color = small_particle_params[i][3];
        glTranslatef(x, y, z);
        if(color == 0) {
            drawSphere(0.1, mat_diffuse_silver, mat_emission_silver, mat_highlight_silver);
        } else {
            drawSphere(0.1, mat_diffuse_blue, mat_emission_blue, mat_highlight_blue);
        }
        glPopMatrix();
    }
    glPopMatrix();
}

void display(void)
{
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glPushMatrix();
		glTranslatef(0, 0, -6);

	    glRotatef(angle2, 1.0, 0.0, 0.0);
		glRotatef(angle, 0.0, 1.0, 0.0);

		glScalef(zoom,zoom,zoom);

		switch (current_object) {
            case 0:
                drawSphere(1, mat_diffuse_blue, mat_emission_blue, mat_highlight_blue);
                break;
            case 1:
                drawCylinder(1, 2, mat_diffuse_silver, mat_emission_silver, mat_highlight_silver);
                break;
            case 2:
                // a sheet of pills
                glScalef(0.3,0.3,0.3);
                for (int i = -4; i < 4; i+=5) {
                    for (int j = -4; j < 8; j+=3) {
                        glPushMatrix();
                        glTranslatef(i, j, 0);
                        drawFullPill();
                        glPopMatrix();
                    }
                }
                break;
            case 3:
                // a pill that has been spilled
                glScalef(0.7,0.7,0.7);
                // small particles
                drawSmallSpheres();
                
                // left half
                glTranslatef(-1.5, 0, 0);
                drawLeftPill();
                
                // right half
                glTranslatef(2, 0, 0);
                drawRightPill();
                
                break;
            default:
                break;
		};
	glPopMatrix();
	glutSwapBuffers ();
}




void keyboard (unsigned char key, int x, int y)
{
	switch (key) {
	case 'p':
	case 'P':
		glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
		break;			
	case 'w':
	case 'W':
		glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
		break;			
	case 'v':
	case 'V':
		glPolygonMode(GL_FRONT_AND_BACK,GL_POINT);
		break;			
	case 's':
	case 'S':
		m_Smooth = !m_Smooth;
		break;
	case 'h':
	case 'H':
		m_Highlight = !m_Highlight;
		break;

	case '1':
	case '2':
	case '3':
	case '4':
		current_object = key - '1';
		break;

	case 27:
		exit(0);
		break;
		
	default:
	break;
	}

	glutPostRedisplay();
}



void
mouse(int button, int state, int x, int y)
{
  if (state == GLUT_DOWN) {
	mouseButton = button;
    moving = 1;
    startx = x;
    starty = y;
  }
  if (state == GLUT_UP) {
	mouseButton = button;
    moving = 0;
  }
}

void motion(int x, int y)
{
  if (moving) {
	if(mouseButton==GLUT_LEFT_BUTTON)
	{
		angle = angle + (x - startx);
		angle2 = angle2 + (y - starty);
	}
	else zoom += ((y-starty)*0.001);
    startx = x;
    starty = y;
	glutPostRedisplay();
  }
  
}

int main(int argc, char **argv)
{
	cout<<"CS3241 Lab 3"<< endl<< endl;

	cout << "1-4: Draw different objects"<<endl;
	cout << "S: Toggle Smooth Shading"<<endl;
	cout << "H: Toggle Highlight"<<endl;
	cout << "W: Draw Wireframe"<<endl;
	cout << "P: Draw Polygon"<<endl;
	cout << "V: Draw Vertices"<<endl;
	cout << "ESC: Quit" <<endl<< endl;

	cout << "Left mouse click and drag: rotate the object"<<endl;
	cout << "Right mouse click and drag: zooming"<<endl;

	glutInit(&argc, argv);
	glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE);
	glutInitWindowSize (600, 600);
	glutInitWindowPosition (50, 50);
	glutCreateWindow ("CS3241 Assignment 3");
	glClearColor (1.0,1.0,1.0, 1.0);
    
    generateSmallParticlesParams();
    
	glutDisplayFunc(display);
	glutMouseFunc(mouse);
	glutMotionFunc(motion);
	glutKeyboardFunc(keyboard);
	setupLighting();
	glDisable(GL_CULL_FACE);
	glEnable(GL_DEPTH_TEST); 
	glDepthMask(GL_TRUE);

    glMatrixMode(GL_PROJECTION);
    gluPerspective( /* field of view in degree */ 40.0,
  /* aspect ratio */ 1.0,
    /* Z near */ 1.0, /* Z far */ 80.0);
	glMatrixMode(GL_MODELVIEW);
	glutMainLoop();

	return 0;
}
