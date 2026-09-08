PROGRAM MAIN

  IMPLICIT NONE

  REAL X(200),Y(200)

  INTEGER PUNTOS,I
 
PUNTOS=121
OPEN (10,FILE='contorno_Hurd.txt')

DO I=1,PUNTOS
	READ (10,*)X(I),Y(I)
ENDDO

CLOSE (10)

OPEN (10,FILE='mesh_Hurd_gmsh_2D_50.geo')

DO I=1,PUNTOS
	WRITE(10,*)'Point(',I,') = {',X(I),',',Y(I),',',0,',',50,'};'
ENDDO
DO I=1,PUNTOS-1
	WRITE(10,*)'Line(',I,') = {',I,',',I+1,'};'
ENDDO
WRITE(10,*)'Line(',PUNTOS,') = {',PUNTOS,',',1,'};'

CLOSE (10)

  STOP
END PROGRAM MAIN


