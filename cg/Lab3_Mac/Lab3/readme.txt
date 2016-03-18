Matric Number: A0093910H

Pills

Primitives used:

glBegin(GL_POLYGON);
glVertex3d()
glNormal3d()
glEnd()
glPushMatrix()
glPopMatrix()

Transformations used:
glTranslatef()
glRotatef()
glScalef()

Method modified:
display()
main() - added generateSmallParticlesParams() to randomize positions for small particles
main() - added GLUT_MULTISAMPLE for anti aliasing

Material for objects:
GL_EMISSION and GL_SPECULAR are defined to be similar to GL_DIFFUSE to give the metallic material for the objects
GL_SHININESS is defined as 80 to give shiny material for the objects

Coolest thing:
Composite object 1 is called "a sheet of pills".
Composite object 2 is called "a pill that has been spilled".
Small particles in Composite object 2 look like they have been spilled out.
Metallic effect for the primitive objects

Any other things: