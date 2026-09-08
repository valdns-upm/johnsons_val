PROGRAM MAIN
  ! Adapted from preprocess_GMSH.f90 (Hurd) for Johnsons, using the corrected
  ! boundary contour (roca/div/front, single continuous closed loop) instead
  ! of a single-size contour file. Finer mesh size on the front segment
  ! (code 2) to fix the coarse/low-connectivity front found in
  ! mesh_Johnson_gmsh_2D_100 - see docs/line_search_diagnosis.md.

  IMPLICIT NONE

  REAL X(1300), Y(1300)
  INTEGER CODE(1300)
  REAL SIZE_ROCA_DIV, SIZE_FRONT, PTSIZE
  INTEGER PUNTOS, I

  PUNTOS = 190
  SIZE_ROCA_DIV = 100.0
  SIZE_FRONT = 20.0

  OPEN (10, FILE='Johnsons_boundaries_resampled.txt')
  DO I = 1, PUNTOS
     READ (10,*) X(I), Y(I), CODE(I)
  ENDDO
  CLOSE (10)

  OPEN (10, FILE='mesh_Johnson_gmsh_2D_100_front_refined.geo')

  DO I = 1, PUNTOS
     IF (CODE(I) == 2) THEN
        PTSIZE = SIZE_FRONT
     ELSE
        PTSIZE = SIZE_ROCA_DIV
     ENDIF
     WRITE(10,*) 'Point(',I,') = {',X(I),',',Y(I),',',0,',',PTSIZE,'};'
  ENDDO
  DO I = 1, PUNTOS-1
     WRITE(10,*) 'Line(',I,') = {',I,',',I+1,'};'
  ENDDO
  WRITE(10,*) 'Line(',PUNTOS,') = {',PUNTOS,',',1,'};'

  WRITE(10,*) 'Line Loop(1) = {1:',PUNTOS,'};'
  WRITE(10,*) 'Plane Surface(1) = {1};'

  ! Group boundary lines by contour code so ElmerGrid gets 3 clean BCs
  ! (roca=1, div=2, front=3) instead of one per line - line I uses the
  ! code of its starting point I.
  CALL WritePhysicalLine(10, 1, 0, CODE, PUNTOS)
  CALL WritePhysicalLine(10, 2, 1, CODE, PUNTOS)
  CALL WritePhysicalLine(10, 3, 2, CODE, PUNTOS)
  WRITE(10,*) 'Physical Surface(1) = {1};'

  CLOSE (10)

  STOP
END PROGRAM MAIN

SUBROUTINE WritePhysicalLine(UNIT, PHYSID, MATCHCODE, CODE, PUNTOS)
  IMPLICIT NONE
  INTEGER :: UNIT, PHYSID, MATCHCODE, PUNTOS
  INTEGER :: CODE(PUNTOS)
  INTEGER :: I
  LOGICAL :: FIRST

  FIRST = .TRUE.
  WRITE(UNIT,'(A,I0,A)',ADVANCE='NO') 'Physical Line(',PHYSID,') = {'
  DO I = 1, PUNTOS
     IF (CODE(I) == MATCHCODE) THEN
        IF (.NOT. FIRST) WRITE(UNIT,'(A)',ADVANCE='NO') ','
        WRITE(UNIT,'(I0)',ADVANCE='NO') I
        FIRST = .FALSE.
     ENDIF
  ENDDO
  WRITE(UNIT,'(A)') '};'
END SUBROUTINE WritePhysicalLine
