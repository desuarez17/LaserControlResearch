
% Number of cells per side (match the SW model)
n = 5;
numParams = n^2;

% random values between -1.75 and 1.75
newValues = rand(1,25)*3.5-1.75; 

%Remove corners from param set
newValues(1) = 0;
newValues(n) = 0;
newValues(n^2-n+1) = 0;
newValues(n^2) = 0;

apdlFileName = 'set_displacement.apdl';
fileID = fopen(apdlFileName, 'w');

fprintf(fileID, '! Set Delection of each cell (0-3.5 micro meter)\n');
fprintf(fileID, '/PREP7\n'); 

% Create each param for deflection of cell
for i = 1:numParams
    paramName = sprintf('P%d', i); %P1=newValues(i)
    fprintf(fileID, '*SET, %s, %f\n', paramName, newValues(i)); 
end

fprintf(fileID, 'FINISH\n');  
fclose(fileID);

disp(['APDL script "', apdlFileName, '" created successfully.']);
