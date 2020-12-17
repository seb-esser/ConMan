function checkNodeConnectivity(adjMtx)

fprintf('Check connectivity of all nodes: \n'); 
fprintf('- Rows - \n');
for i = 1:size(adjMtx, 1)
   % get vector
   connectionsOfNode = adjMtx(i,:); 
   isConnected = ismember(1, connectionsOfNode); 
   if isConnected
       fprintf('\t Node %3d has a connection to the graph. \n', i-1); 
   else
       fprintf('\t Node %3d has no children. \n', i-1);
   end
end

fprintf('- Columns - \n');
for i = 1:size(adjMtx, 2)
   % get vector
   connectionsOfNode = adjMtx(:,i); 
   isConnected = ismember(1, connectionsOfNode); 
   if isConnected
       fprintf('\t Node %3d has a connection to the graph. \n', i-1); 
   else
       fprintf('\t Node %3d has no parents. \n', i-1);
   end
end

fprintf('\n');
end

