%%% If you want to generate dynamo euler angles from matrices which
%%% align references to particles
%%% (the matrices you use to visualise aligned z vectors)
%%% use:
%   matrix2euler zxz intrinsic positive_ccw
%   on the transpose of the matrix

%%% If you want to generate matrices which align references to particles
%%% from dynamo euler angles
%%% use:
%   euler2matrix zxz extrinsic positive_ccw
%   then transpose the matrix/matrices


%%% Understanding what Dynamo euler angles represent

% As a user, we have access to (and need to generate) euler angles in a
% table file (*.tbl)

% what do these angles represent?
% tdrot (rotation around z in degrees)
% tilt (rotation around new x in degrees)
% narot (rotation around new z in degrees)

% This description implies an intrinsic coordinate system
% R = Rz(tdrot) * Rx(tilt) * Rz(narot)

% Is this for rotating the reference or the particle?
p = [0;0;1];
m = dynamo_euler2matrix([0,90,0]);

new_p = m * p;

% [0;0;1] became [0;-1;0] after premultiplication by matrix from
% dynamo_euler2matrix

% This means that positive rotations (like our 90) correspond to CCW
% rotations when looking from positive x towards the origin

% let's do a different one
eulers = [30, 60, 90];
matrix = dynamo_euler2matrix(eulers);

% matrix
% [-0.250000000000000,-0.433012701892220,0.866025403784439;
%  0.866025403784439,-0.500000000000000,-5.30287619362453e-17;
%  0.433012701892219,0.750000000000000,0.500000000000000]

% in my eulerangles package, matrix2zxz_extrinsic of the above matrix
% yields [30, 60, 90]

% in my eulerangles package, the following:
% euler2matrix([30, 60, 90], axes='zxz', extrinsic=True, positive_ccw=True)
% yields

% array([[-2.50000000e-01, -4.33012702e-01,  8.66025404e-01],
%       [ 8.66025404e-01, -5.00000000e-01, -5.30287619e-17],
%       [ 4.33012702e-01,  7.50000000e-01,  5.00000000e-01]])

% this implies that dynamo_euler2matrix generates rotation matrices as
% though the euler angles were zxz extrinsic angles

% this is corrobrated by dynamo_angles2orientations.m

north=[0;0;1];
for r = 1:size(angles,1);
   m = dynamo_euler2matrix(angles(r,:));
   north_rotated=m'*north;
   orientations(r,:)=north_rotated';
end

% this basically says that dynamo uses the inverse of the matrix generated
% by dynamo_euler2matrix to rotate references aligned along z onto particles

% SUMMARY
% dynamo_euler2matrix produces zxz extrinsic positive ccw rotation matrices
% these matrices align rotated aligned particles onto a reference
% the inverse of these aligns references (along z) with
% aligned particles