% Sebastian Esser - TUM CMS 
% Some tests for graph representations of common data models

%% clear
clear; 
fprintf('\n'); 

addpath('adjMtx_tests\'); 

%% --- Load record-json from Neo4j ---
filename = "AdjMtx_wouLoop_unconnectedSample.json";  %change filename here
txt = fileread(filename);

% parse to matlab struct
values = jsondecode(txt);

% init mtx
adjMtx = zeros(sqrt(length(values)));

% parse records to mtx
for i = 1:length(values)
    % shift by 1: MATLAB starts counting at 1!
    rowIndex = values(i).('ID_n_') + 1;
    colIndex = values(i).('ID_m_') + 1;
    mtxVal = values(i).('connected');
    
    % write to adjMtx
    adjMtx(rowIndex, colIndex) = mtxVal;
end

%% --- adjMtx checks ---
% check main Diagonale of adjMtx
checkDiag(adjMtx); 

% symmetry
checkSymmetry(adjMtx); 

% find unconnected nodes
checkNodeConnectivity(adjMtx);

% check regularity and degrees
checkRegularity(adjMtx); 

