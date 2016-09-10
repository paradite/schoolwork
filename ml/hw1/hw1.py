import numpy as np
import numpy.random as nr
import matplotlib.pyplot as pl
# Plotting with style! 
import seaborn as sb 

# Size the plot appropriately for online display
pl.rcParams['figure.figsize'] = (12.0, 10.0)

nr.seed(3244)

# load datasets code

import pandas as pd
import math

def add_bias_column(x):
    return np.insert(x, 0, 1, axis=1)

input_dimension = 20
weight_dimension = input_dimension + 1 # add bias
training_data = pd.read_table('hw1-train.dat', delim_whitespace=True, header=None)
x_input = training_data.values[:,:input_dimension]
y_input = training_data.values[:,input_dimension]
N = len(x_input)
x_input = add_bias_column(x_input)

# LR code

def compute_single_point_gradient(xi, yi, current_w):
    numerator = yi * xi
    denominator = 1 + math.exp(yi * current_w.dot(xi))
    return (numerator / denominator)

def compute_ave_gradient(xn, yn, current_w):
    gradient_sum = np.zeros(weight_dimension)
    for idx in range(N):
        gradient_sum += compute_single_point_gradient(xn[idx], yn[idx], current_w)
    ave_gradient = (-1 / N) * gradient_sum
    return ave_gradient

def compute_new_weight(ave_gradient, current_w, eta):
    return current_w + eta * (ave_gradient * (-1))

def lr(current_w, eta, use_single_point = False, iteration_number = 0):
    if use_single_point:
        idx = iteration_number % N
        gradient = -compute_single_point_gradient(x_input[idx], y_input[idx], current_w)
    else:
        gradient = compute_ave_gradient(x_input, y_input, current_w)
    return compute_new_weight(gradient, current_w, eta)

def compute_single_in_sample_error(xi, yi, current_w):
    return np.log(1 + math.exp((-yi) * current_w.dot(xi)))

def compute_ave_in_sample_error(xn, yn, current_w):
    err_sum = 0
    for idx in range(N):
        err_sum += compute_single_in_sample_error(xn[idx], yn[idx], current_w)
    err_ave = (1 / N) * err_sum
    return err_ave

def learn_batch(iterations, eta):
    print('batch learning with ' + str(iterations) + ' iterations and eta of ' + str(eta))
    w = np.zeros(weight_dimension)
    for x in range(iterations):
        w = lr(w, eta, False)
        if(x % 1000 == 0 and x > 0):
            print('completed ' + str(x) + ' iterations')
        # print(w)
        # print(compute_ave_in_sample_error(x_input, y_input, w))
    return w

def learn_single_point(iterations, eta):
    print('single point learning with ' + str(iterations) + ' iterations and eta of ' + str(eta))
    w = np.zeros(weight_dimension)
    for x in range(iterations):
        w = lr(w, eta, True, x)
        if(x % 1000 == 0 and x > 0):
            print('completed ' + str(x) + ' iterations')
        # print(w)
        # print(compute_ave_in_sample_error(x_input, y_input, w))
    return w

w1 = learn_batch(2333, 0.05)
w2 = learn_batch(2333, 0.005)
w3 = learn_single_point(2333, 0.05)
w4 = learn_single_point(2333, 0.005)

# Evaluation code
testing_data = pd.read_table('hw1-test.dat', delim_whitespace=True, header=None)
x_test = testing_data.values[:,:input_dimension]
x_test = add_bias_column(x_test)
y_test = testing_data.values[:,input_dimension]
N_test = len(x_test)

def check_weight_against_test(weight, test_xi, test_yi):
    dot_product = weight.dot(test_xi)
    # print(dot_product)
    h_x = math.exp(dot_product) / (1 + math.exp(dot_product))
    prediction = 1 if (h_x >= 0.5) else -1
    # print(prediction == test_yi)
    return (prediction == test_yi)

def compute_out_of_sample_error(weight):
    err_sum = 0
    for idx in range(N_test):
        if(check_weight_against_test(weight, x_test[idx], y_test[idx]) != True):
            err_sum += 1
    err_ave = (1 / N_test) * err_sum
    return err_ave

def print_result(weight):
    print('weight')
    print(weight.tolist())
    # print('in-sample error')
    # print(compute_ave_in_sample_error(x_input, y_input, weight))
    print('out-sample error')
    print(compute_out_of_sample_error(weight))

print_result(w1)
print_result(w2)
print_result(w3)
print_result(w4)

# Plotting (if any) code