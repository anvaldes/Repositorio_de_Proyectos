%% Defina el valor de bound desde la línea de comando!
%% por ejemplo clingo -c bound=15 parte1.lp
time(1..bound).

% hay 5 acciones posibles
move_action(up).
move_action(down).
move_action(left).
move_action(right).
wait_action(wait).
action(A) :- move_action(A).
action(A) :- wait_action(A).

% on(R,X,Y,T) expresa que el robot R está en (X,T)
% en el tiempo T
% TAREA - PARTE 1b): modifique las siguientes líneas para obtener
% un grounding más eficiente

on(R,X,Y+1,T+1) :- exec(R,up,T),on(R,X,Y,T),time(T+1), rangeX(X), rangeY(Y+1).
on(R,X,Y-1,T+1) :- exec(R,down,T),on(R,X,Y,T),time(T+1), rangeX(X), rangeY(Y-1).
on(R,X-1,Y,T+1) :- exec(R,left,T),on(R,X,Y,T),time(T+1), rangeX(X-1), rangeY(Y).
on(R,X+1,Y,T+1) :- exec(R,right,T),on(R,X,Y,T),time(T+1), rangeX(X+1), rangeY(Y).
on(R,X,Y,T+1)   :- exec(R,wait,T),on(R,X,Y,T),time(T+1), rangeX(X), rangeY(Y).


% TAREA - PARTE 1a): defina el predicado
% stopped_at_goal(R,T): para expresar que R está en el objetivo
% en tiempo T, T+1, T+2, ..., bound

stopped_at_goal(R,T) :- time(T), robot(R), goal(R,X,Y), {on(R,X,Y,T_1): time(T_1), T_1>=T, T_1<=bound} = bound-T.

% TAREA - PARTE 1a): escriba una expresión de minimización o
% maximización para expresar que
% se detienen en su objetivo lo antes posible

#minimize {T, R: stopped_at_goal(R,T)}.

% cada robot puede ejecutar exactamente una acción en cada instante de tiempo
1 { exec(R,A,T) : action(A)} 1 :- robot(R),time(T+1).

% Escriba las restriciones que considere necesarias
% suponiendo que:
% rangeX(W): W está dentro del rango del eje X
% rangeY(W): W está dentro del rango del eje Y

%% Robots no pueden salir de la grilla
:- on(R,X,Y,T),not rangeX(X).
:- on(R,X,Y,T),not rangeY(Y).

%% Robots no pueden atravesar obstaculos
:- on(R,X,Y,T), obstacle(X,Y).
%% No pueden superponerse
:- on(R1, X, Y, T), on(R2, X, Y, T), R1!=R2.
%% No pueden intercambiar sus posiciones
:- on(R1,X,Y,T),on(R2,X+1,Y,T),on(R2,X,Y,T+1),on(R1,X+1,Y,T+1).
:- on(R1,X,Y,T),on(R2,X,Y+1,T),on(R2,X,Y,T+1),on(R1,X,Y+1,T+1).


% goal(R,X,Y,T): definido solo por compatibilidad con el
% visualizador
goal(R,X,Y,T) :- goal(R,X,Y),time(T).
goal(R,X,Y,0) :- goal(R,X,Y).

% at_goal(R,T) expresa
% que el robot R está en su objetivo en el tiempo T
at_goal(R,T) :- on(R,X,Y,T),goal(R,X,Y).

% En términos de at_goal, defina una restricción
% expresando que todo robot debe llegar al objetivo
:- robot(R), not at_goal(R,bound).

#show on/4.
#show obstacle/2.
#show rangeX/1.
#show rangeY/1.
#show exec/3.
#show goal/4.
