from fourier import *

import numpy as np
import sys
from scipy.fftpack import fftshift, fft2, ifft2, ifftshift, fft, ifft
#import nufft

#output, array type:complex, dim:num_row*2,num_columns
		#with second half =0
#f0: the average frequency you scaled
def main( baseline=257,freq='00',f0=322.5,pol='LL',pad='no'):
	print 'Band selected: ' + freq
	infile = '/mnt/scratch-lustre/simard/B0834_2012/Gate0/gb057_1.input_baseline'+str(baseline)+'_freq_'+str(freq)+'_pol_'+pol+'.rebint'
	outfile = '/mnt/raid-cita/dzli/gb057/Gate0/gb057_baseline'+str(baseline)+'_freq_'+str(freq)+'_pol_'+pol+'_f0_'+str(f0)+'_nopad.rebint'

	multigate_path = '/mnt/raid-cita/dzli/gb057/multigate/'
	multigate_name = 'tot_gb057_1.input_baseline257_freq_00.rebint'
	infile = multigate_path+'sn'+multigate_name
	outfile=multigate_path+'gb057_baseline'+str(baseline)+'_freq_'+str(freq)+'_f0_'+str(f0)+'_nopad.rebint'


	if freq=='00':
		initial_frequency = 310.5 #MHz
	elif freq=='01':
		initial_frequency = 318.5 #MHz
	elif freq=='02':
		initial_frequency = 326.5 #MHz
	elif freq=='03':
		initial_frequency = 334.5 #MHz
	else:
		print 'Invalid frequency'

	num_rows = 16384
	num_columns = 1321
	bandwidth = 8.
	band_per_channel = bandwidth/num_rows
	frequency = np.arange(num_rows)*band_per_channel + initial_frequency
	timespan = 6729 #ks
	time_resolution = timespan/num_columns 
	time = np.arange(num_columns)*time_resolution

	I = np.fromfile(infile,dtype=np.float32).reshape(num_columns,num_rows).T

	if pad=='y':
		Ipad = np.pad(I,((0,num_rows),(0,0)),'constant',constant_values=0)
		I = Ipad
		del Ipad
	# Set zeros to the mean - move to after zero padding to include
		mean = np.mean(I)*np.size(I)/(np.count_nonzero(I)) #mean excluding zeros
		for i in range(num_columns):
			if np.sum(I[:,i])==0.:
				I[:,i] = mean

	# Slow FT the time axis
	Iout = np.ones(I.shape,dtype=complex)
	print Iout.shape
	for i in range(len(frequency)):
		x = I[i,:]
		N = x.shape[0]
		n = np.arange(N) - N/2
		k = n.reshape((N,1))*frequency[i]/f0
		M = np.exp(-2.0j*np.pi*k*n/N)
		y = np.dot(M,x)
		
		# Slow FT back

		k = n.reshape((N,1))
		M = np.exp(2.0j*np.pi*k*n/N)
		Iout[i,:] = 1./N*np.dot(M,y)

	  
	print 'Writing output to ' + outfile
	Iout.tofile(outfile)
#change saving method to be conformal with ueli's
	return

if __name__=='__main__':
    if len(sys.argv)>3:
        main( sys.argv[1], sys.argv[2],float(sys.argv[3]))
    else:
        print '\nslowft_time.py requires command line arguments:\n\nconvolution.py baseline freq f0\n\nbaseline can be any of 257 258 or 514\nfreq can be any of 00 01 02 or 03\n'
        # later, buid in ability to use 2 or 1 frequency bands (ie. merge bands)
