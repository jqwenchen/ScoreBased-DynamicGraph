import numpy as np
W_est = []
W_est_1 = np.array([[3.0, 2.0], [1.0, 1.4]])
W_est_2 = np.array([[4.0, 5.0], [2.0, 1.6]])
W_est.append(W_est_1)
W_est.append(W_est_2)

W_est_arr = np.array(W_est)
leng = len(W_est_arr)
sum_arr = ([[0.0, 0.0], [0.0, 0.0]])
for i in range(len(W_est_arr)):
    arr = W_est_arr[i]
    sum_arr[0][0] += arr[0][0]
    sum_arr[0][1] += arr[0][1]
    sum_arr[1][0] += arr[1][0]
    sum_arr[1][1] += arr[1][1]

sum_arr[0][0] = sum_arr[0][0] / leng
sum_arr[0][1] = sum_arr[0][1] / leng
sum_arr[1][0] = sum_arr[1][0] / leng
sum_arr[1][1] = sum_arr[1][1] / leng

print(sum_arr)