function  checkRegularity(adjMtx)

fprintf('Check regularity and degrees of nodes \n'); 

% calc Degree vor each node
for i = 1:size(adjMtx, 1)
    incomingDeg(i) = sum(adjMtx(:, i)); 
end
for i = 1:size(adjMtx, 2)
    outgoingDeg(i) = sum(adjMtx(i, :)); 
end
    
fprintf('incoming degree: ');
disp(incomingDeg); 
fprintf('outgoing degree: ');
disp(outgoingDeg); 

% compare the degrees of all nodes: regular graph?
% reg = minDegree == maxDegree; 
end

