function checkSymmetry(adjMtx)

fprintf('Check symmetry of adjacency matrix: \n'); 
isSymmmetric = issymmetric(adjMtx); 

if isSymmmetric
    fprintf('\t -> Symmetrical adjacency matrix \n');
else
    fprintf('\t -> Unsymmetrical adjacency matrix -> directed graph \n');
end

fprintf('\n');

end

