import sys, os
sys.path.append('../')
import numpy as np
from itertools import product
from pinn_api import predict_ids_grads, predict_ids
import matplotlib.pyplot as plt
import glob

## ------------  Input  ---------------
VDS = None
VTG = 0.1
VBG = 0.1
## ------------  True data  ---------------
ids_file = glob.glob('./transiXOR_data/current_D9.npy')
data_true = np.load(ids_file[0])
## ------------  Helper Funs  ---------------
def ids(data, vds=None, vbg=None, vtg=None):
	# vds, vbg, vtg, id
	# assume v from -0.1 to 0.3, total 41 points
	vid = lambda v : int(round((v + 0.1)/0.01))
	if vds and vbg:
		return data[vid(vds), vid(vbg), :]
	if vtg and vbg:
		return data[:, vid(vbg), vid(vtg)]
	else:
		raise Exception('Not Supported')

def plot(data_pred, data_true=None, vds=None, vbg=None, vtg=None):
	plt.plot(ids(data_pred, vds=vds, vbg=vbg, vtg=vtg), 'r')
	if data_true is not None:
		plt.plot(ids(data_true, vds=vds, vbg=vbg, vtg=vtg), 'b')
	plt.show()
	plt.semilogy(ids(data_pred, vds=vds, vbg=vbg, vtg=vtg), 'r')
	if data_true is not None:
		plt.semilogy(ids(data_true, vds=vds, vbg=vbg, vtg=vtg), 'b')
	plt.show()
## ------------  Prediction ---------------
pred_data_path = 'pred_data/'
# model_name = 'bise_ext_sym_h264_0'
model_name = 'bise_ext_sym_h264_neggrad_3'
if not os.path.isfile(pred_data_path + model_name + '.npy'):
	print('Computing all data...')
	vds = np.linspace(-0.1, 0.3, 41)
	vbg = np.linspace(-0.1, 0.3, 41)
	vtg = np.linspace(-0.1, 0.3, 41)
	iter_lst = list(product(vds, vbg, vtg))
	vds_pred = np.expand_dims(np.array([e[0] for e in iter_lst], dtype=np.float32), axis=1)
	vbg_pred = np.array([e[1] for e in iter_lst], dtype=np.float32)
	vtg_pred = np.array([e[2] for e in iter_lst], dtype=np.float32)
	vg_pred = np.column_stack((vtg_pred, vbg_pred))
	vg_pred = np.sum(vg_pred, axis=1, keepdims=True) # model use symmetry vtg vbg
	model_path = './transiXOR_Models/'
	## If trained with adjoint builder
	data_pred_flat, vg_grad_flat, vd_grad_flat = predict_ids_grads(
		model_path + model_name, vg_pred, vds_pred)
	## If trained with origin builder
	# data_pred_flat = predict_ids(
	# 	model_path + model_name, vg_pred, vds_pred)
	data_pred = data_pred_flat.reshape((41, 41, 41))
	vg_grad = vg_grad_flat.reshape((41, 41, 41))
	vd_grad = vd_grad_flat.reshape((41, 41, 41))
	np.save(pred_data_path + model_name + '.npy', data_pred) 
	np.save(pred_data_path + model_name + '_vg_grad.npy', vg_grad) 
	np.save(pred_data_path + model_name + '_vd_grad.npy', vd_grad) 
	plot(data_pred, data_true=data_true, vds=VDS, vbg=VBG, vtg=VTG)
else:
	print('Reading from pre-computed data...')
	data_pred = np.load(pred_data_path + model_name + '.npy')
	vg_grad = np.load(pred_data_path + model_name + '_vg_grad.npy')
	vd_grad = np.load(pred_data_path + model_name + '_vd_grad.npy')
	print(data_pred.shape)
	plot(data_pred, data_true=data_true, vds=VDS, vbg=VBG, vtg=VTG)
	# plot(vg_grad, vds=VDS, vbg=VBG, vtg=VTG)
	plot(vd_grad, vds=VDS, vbg=VBG, vtg=VTG)

## Point test
# ids_pred = predict_ids(
# 	'./transiXOR_Models/bise_ext_sym_h264_0',
# 	np.array([0.2+0.2]), np.array([0.2]))
# print(ids_pred)
# ids_pred = predict_ids(
# 	'./transiXOR_Models/bise_ext_sym_h264_0',
# 	np.array([0.0+0.0]), np.array([0.2]))
# print(ids_pred)
# ids_pred = predict_ids(
# 	'./transiXOR_Models/bise_ext_sym_h264_0',
# 	np.array([0.0+0.1]), np.array([0.2]))
# print(ids_pred)
# ids_pred = predict_ids(
# 	'./transiXOR_Models/bise_ext_sym_h264_0',
# 	np.array([0.1+0.0]), np.array([0.2]))
