function checkDiag(adjMtx)
%CHECKDIAG

% get diag and check circular loops on single node
fprintf('Check diag of adjMtx for occurences of 1: \n');
myDiag = diag(adjMtx);
fprintf('\t mainDiag: \n');
disp(myDiag');

if ismember(1, myDiag)
    fprintf('\t -> Self edges detected! \n');
else
    fprintf('\t -> No self-edges detected. \n'); 
end
fprintf('\n');

end

