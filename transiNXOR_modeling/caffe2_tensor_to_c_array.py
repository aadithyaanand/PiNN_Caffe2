import sys
sys.path.append('../')
import caffe2_paths
from caffe2.python import workspace
from pinn import exporter
from scipy.io import savemat
import numpy as np
import pickle

model_name = 'bise_ext_sym_h264_0'

init_net = exporter.load_init_net('./transiXOR_Models/'+model_name+'_init')
print(type(init_net))
p = {}
with open("c_model/device_param_0","w") as f:
	f.write('/* --------------- MODEL: '+ model_name +' -------------------- */\n')
	for op in init_net.op:
		tensor = workspace.FetchBlob(op.output[0])
		tensor_name = op.output[0].replace('/', '_')
		print(tensor_name)
		print(tensor.shape)
		p[tensor_name] = tensor
		np.set_printoptions(threshold=np.inf)  # force full expr print
		tensor_str = np.array2string(tensor.flatten(), separator=',')
		tensor_str = tensor_str.replace("[", "{").replace("]", "}")
		str = 'static const float ' + tensor_name + '[] = ' + tensor_str + ';\n'
		f.write(str)

	## Preprocess param
	with open("./transiXOR_Models/"+model_name+"_preproc_param.p", "rb") as f:
		preproc_dict = pickle.load(f)
	print(preproc_dict)

## TESTING
def test(vtg, vbg, vds):
	# vg = np.array([[vtg], [vbg]]); 
	vg = np.array([vtg + vbg]) # Symmetry assumption
	vd = np.array([[vds]])
	## (vg - vg_shift)/scale['vg']; vd / scale['vd']
	vg = (vg - 0.2)/0.4; vd /= 0.3

	tanh_temp0 = np.matmul(p['tanh_fc_layer_0_w'], vd)
	sig_temp0 = np.matmul(p['sig_fc_layer_0_w'], vg) + np.expand_dims(p['sig_fc_layer_0_b'], axis=1)
	inter0 = np.matmul(p['inter_embed_layer_0_w'], tanh_temp0) + np.expand_dims(p['inter_embed_layer_0_b'], axis=1)
	sig_temp0 = 1 / (1 + np.exp(-(inter0+sig_temp0)))
	tanh_temp0 = np.tanh(tanh_temp0)

	tanh_temp1 = np.matmul(p['tanh_fc_layer_1_w'], tanh_temp0)
	sig_temp1 = np.matmul(p['sig_fc_layer_1_w'], sig_temp0) + np.expand_dims(p['sig_fc_layer_1_b'], axis=1)
	inter1 = np.matmul(p['inter_embed_layer_1_w'], tanh_temp1) + np.expand_dims(p['inter_embed_layer_1_b'], axis=1)

	sig_temp1 = 1 / (1 + np.exp(-(inter1+sig_temp1)))
	tanh_temp1 = np.tanh(tanh_temp1)
	# print(tanh_temp1)
	tanh_temp2 = np.matmul(p['tanh_fc_layer_2_w'], tanh_temp1)
	sig_temp2 = np.matmul(p['sig_fc_layer_2_w'], sig_temp1) + np.expand_dims(p['sig_fc_layer_2_b'], axis=1)
	inter2 = np.matmul(p['inter_embed_layer_2_w'], tanh_temp2) + np.expand_dims(p['inter_embed_layer_2_b'], axis=1)
	sig_temp2 = 1 / (1 + np.exp(-(inter2+sig_temp2)))
	tanh_temp2 = np.tanh(tanh_temp2)
	## ids = sig_temp2 * tanh_temp2 * scale['id']
	ids = sig_temp2 * tanh_temp2 * 457.86010742

	return ids


