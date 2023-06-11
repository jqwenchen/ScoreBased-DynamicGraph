from locally_connected import LocallyConnected
from lbfgsb_scipy import LBFGSBScipy
from trace_expm import trace_expm
import torch
import torch.nn as nn
import numpy as np

class lasso_MLP(nn.Module):
    def __init__(self, dims, bias=True):
        super(lasso_MLP, self).__init__()
        assert len(dims) >= 2
        assert dims[-1] == 1
        d = dims[0]
        nums = dims[1]
        self.dims = dims
        self.node_nums = nums
        self.p_est = nn.Parameter(torch.Tensor(np.ones((d, d))))

    def forward(self,Xlag,adj):  # [n, d] -> [n, d]
        # M = adj @ Xlag @ P
        M = torch.matmul(adj, Xlag)
        M = torch.matmul(M, self.p_est)
        #M = torch.matmul(Xlag, self.p_est)
        return M

    def h_func(self):
        """Constrain 2-norm-squared of fc1 weights along m1 dim to be a DAG"""
        d = self.dims[0]
        h = trace_expm(self.p_est * self.p_est) - d  # (Zheng et al. 2018)
        return h

    def diag_zero(self):
        diag_loss = torch.trace(self.p_est * self.p_est)
        return diag_loss

def squared_loss(output, target):
    n = target.shape[0] * target.shape[1]
    loss = 0.5 / n * torch.sum((output - target) ** 2)
    return loss

def L1Norm(matrix):
    return  torch.abs(matrix).sum()

def dual_ascent_step(model, Xlags, adj, lambda1, lambda2, rho, alpha, h, rho_max):
    """Perform one step of dual ascent in augmented Lagrangian."""
    h_new = None
    optimizer = LBFGSBScipy(model.parameters())
    #Xlag_torch = torch.from_numpy(Xlag)
    #X_torch = torch.from_numpy(X)
    t=0
    def closure():
        optimizer.zero_grad()
        # X_hat = A@Xlag@P
        X_hat = model(Xlags[:-1], adj)
        loss = squared_loss(X_hat, Xlags[1:])
        primal_obj = loss + lambda1 * L1Norm(model.p_est)
        primal_obj.backward()
        return primal_obj
    optimizer.step(closure)  # NOTE: updates model in-place
    return t

def lasso_model(model: nn.Module,
                      Xlags,
                      adj,
                      lambda1: float = 0.,
                      lambda2: float = 0.,
                      max_iter: int =100,
                      h_tol: float = 1e-8,
                      rho_max: float = 1e+16):
    rho, alpha, h = 1.0, 0.0, np.inf
    for _ in range(max_iter):
        t = dual_ascent_step(model,Xlags, adj, lambda1, lambda2,
                                         rho, alpha, h, rho_max)
    p_est = model.p_est
    p_est = p_est.detach().numpy()
    return p_est

def main():

    torch.set_default_dtype(torch.double)
    np.set_printoptions(precision=3)

    import utils as ut
    ut.set_random_seed(123)

    n, d, s0, graph_type, sem_type = 100, 50, 25, 'ER', 'gauss'

    # 载入Xlag
    X = np.loadtxt("X.csv", delimiter=",")

    # 载入Xlag
    Xlag = np.loadtxt("Xlags.csv", delimiter=",")# 此处的X维度一定要和上面设置的n d对的上
    model = lasso_MLP(dims=[d, n, 1], bias=True)

    # 载入adj
    adj = np.loadtxt("adj.csv", delimiter=",")  # 此处的X维度一定要和上面设置的n d对的上
    adj = torch.Tensor(adj)

    # 载入p_mat
    p_true = np.loadtxt("p_true.csv", delimiter=",")  # 此处的X维度一定要和上面设置的n d对的上

    p_est  = lasso_model(model, X, Xlag, adj, lambda1=0.01, lambda2=0.01)
    p_est_ = p_est

    print("****************lasso***********")
    print("p_est:")
    w_threshold = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8,0.9,1.0,1.1,1.2,1.3]
    for thre in w_threshold:
        p_est_[np.abs(p_est_) < thre] = 0
        acc = ut.count_accuracy(p_true, p_est_ != 0)
        print("w_threshold = ", thre,acc)
        p_est_ = p_est


if __name__ == '__main__':
    main()
