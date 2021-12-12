%#const bound = 8.
time(1..bound).

% hay 5 acciones posibles
move_action(up).
move_action(down).
move_action(left).
move_action(right).
wait_action(wait).
swap_action(swap(R)) :- robot(R).
action(A) :- move_action(A).
action(A) :- wait_action(A).
action(A) :- swap_action(A).

% suponga que exec(R,A,T) expresa que R \
% ejecuta la accion A en T

% on(R,X,Y,T) expresa que el robot R está en (X,T)
% en el tiempo T
on(R,X,Y+1,T+1) :- exec(R,up,T),on(R,X,Y,T),time(T+1).
on(R,X,Y-1,T+1) :- exec(R,down,T),on(R,X,Y,T),time(T+1).
on(R,X-1,Y,T+1) :- exec(R,left,T),on(R,X,Y,T),time(T+1).
on(R,X+1,Y,T+1) :- exec(R,right,T),on(R,X,Y,T),time(T+1).
on(R,X,Y,T+1)   :- exec(R,wait,T),on(R,X,Y,T),time(T+1).
%%!!!!
% TAREA - PARTE 2a): define el predicado on para cuando un
% robot ejecuta la acción swap

% cada robot puede ejecutar exactamente una acción en cada instante de tiempo
1 { exec(R,A,T) : action(A)} 1 :- robot(R),time(T+1).
% TAREA - PARTE 2e): agrega un restricción adicional
% que expresa que cada robot puede hacer a lo más un swap

%P2a)
on(R,X,Y,T+1) :- exec(R,swap(R1),T), on(R,X,Y,T), time(T+1), rangeX(X), rangeY(Y).

%P2b)
%INERCIA
ha_hecho_swap(R,T) :- exec(R, swap(R1), T), robot(R1), time(T).
goal(R,X,Y,T+1):- not ha_hecho_swap(R,T), robot(R), time(T+1), goal(R,X,Y,T).

%SWAP
goal(R,X1,Y1,T+1) :- exec(R, swap(R1), T), time(T+1), goal(R1,X1,Y1,T).

%P2c)
adyacentes(R1,R2,T) :- on(R1,X-1,Y,T), on(R2,X,Y,T).
adyacentes(R1,R2,T) :- on(R1,X+1,Y,T), on(R2,X,Y,T).
adyacentes(R1,R2,T) :- on(R1,X,Y+1,T), on(R2,X,Y,T).
adyacentes(R1,R2,T) :- on(R1,X,Y-1,T), on(R2,X,Y,T).

%P2d)
exec(R1,swap(R2), T) :- exec(R2,swap(R1),T).
:- exec(R1,swap(R2),T), not adyacentes(R1,R2,T).

%P2e)
0 {exec(R, swap(R1), T): time(T), robot(R1)} 1 :- robot(R).

%% Si necesitas hacer debugging, las siguientes
%% lineas obligan a que se produzca cierto comportamiento
%% Comenta las restricciones de tu programa que no se acomoden a esta
%% especificación para que tu programa tenga modelo!
%% las líneas de abajo definen una solución que usa swaps
%% en el problema prob1.lp adjunto al paquete de la tarea
%exec(R,wait,T)     :- robot(R),time(T+1), T>=7.
%exec(R,up,T)       :- R=1..4,T=0..2.
%exec(R,swap(Rp),3) :- R=1..4,Rp=R+4.
%exec(R,down,T)     :- R=1..4,T=4..6.
%exec(R,swap(Rp),3) :- R=5..8,Rp=R-4.
%exec(R,down,T)     :- R=5..8,T=0..2.
%exec(R,up,T)       :- R=5..8,T=4..6.

%%%!!!

% TAREA - PARTE 2c): escribe el predicado adyacentes(R1,R2,T)
% TAREA - PARTE 2d): escribe restricciones que la acción swap solo
% ocurre entre agentes adyacentes y que es recíproca

%% Robots no pueden salir de la grilla
:- on(R,X,Y,T), not rangeX(X).
:- on(R,X,Y,T), not rangeY(Y).
%% Robots no pueden atravesar obstaculos
:- on(R,X,Y,T), obstacle(X,Y).
%% No pueden superponerse
:- on(R1, X, Y, T), on(R2, X, Y, T), R1!=R2.
%% No pueden intercambiar sus posiciones
:- on(R1, X, Y, T), on(R2, X+1, Y, T), on(R2, X, Y, T+1),on(R1, X+1, Y, T+1).
:- on(R1, X, Y, T), on(R2, X, Y+1, T), on(R2, X, Y, T+1),on(R1, X, Y+1, T+1).

% goal(R,X,Y,T): el objectivo del robot R es (X,Y) en tiempo T
% TAREA - PARTE 2b): termina de escribir el predicado goal(R,X,T,T)
% faltan reglas que dice qué pasa cuando dos robots hacen swap
goal(R,X,Y,0) :- goal(R,X,Y).


% at_goal(R,T) expresa
% que el robot R está en su objetivo en el tiempo T
at_goal(R,T) :- on(R,X,Y,T),goal(R,X,Y,T).

% En términos de at_goal, defina una restricción
% expresando que todo robot debe llegar al objetivo
:- robot(R), not at_goal(R,bound).


#show on/4.
#show obstacle/2.
#show rangeX/1.
#show rangeY/1.
#show exec/3.
#show goal/4.
