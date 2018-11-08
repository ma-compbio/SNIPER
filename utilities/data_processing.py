import os
import numpy as np

from subprocess import call
from scipy.io import loadmat, savemat
from utilities.interchromosome_matrix import construct

def constructAndSave(tmp_dir,prefix):
	M = construct(tmp_dir, prefix=prefix)

	if save_matrix:
		savemat(os.path.join(tmp_dir,'%s_matrix.mat' % prefix),{'inter_matrix' : M})

def hicToMat(h,tmp_dir='.',prefix='hic',autoremove=False,overwrite=False,save_matrix=False,verbose=False):
	try:
		os.stat(tmp_dir)
	except:
		os.mkdir(tmp_dir)

	""" Calls juicer_tools to extract hic data into txt files """
	for chrm1 in range(1,23,2):
		for chrm2 in range(2,23,2):
			output_path = os.path.join(tmp_dir,'{2}_chrm{0}_chrm{1}.txt'.format(chrm1,chrm2,prefix))
			
			if os.path.isfile(output_path) and not overwrite:
				continue

			cmd = 'juicer_tools dump observed KR {0} {1} {2} BP 100000 {3} > tmp_juicer_log'.format(h,chrm1,chrm2,output_path)

			call([cmd],shell=True)

	""" File path of the inter-chromosomal matrix """
	M_filepath = os.path.join(tmp_dir,'%s_matrix.mat' % prefix)

	""" If overwrite flag is set, reconstruct matrix and check save flag """
	if overwrite:
		M = constructAndSave(tmp,prefix)
	else:
		""" If overwrite unset, check if filepath exists and either load mat or construct new """
		if os.path.isfile(M_filepath):
			M = loadmat(M_filepath)['inter_matrix']
		else:
			M = constructAndSave(tmp,prefix)

	""" If autoremove is set, remove hic .txt files """
	if autoremove:
		for chrm1 in range(1,23,2):
			for chrm2 in range(2,23,2):
				file_path = os.path.join(tmp_dir,'chrm{0}_chrm{1}.txt'.format(chrm1,chrm2))
				try:
					os.remove(file_path)
				except:
					continue
	return M

""" Trims sparse, NA, and B4 regions """
def trimMat(M,indices):
	delR, delC = indices['delR'].flatten(), indices['delC'].flatten()
	NA_indices_r, NA_indices_c = indices['NA_indices_r'].flatten(), indices['NA_indices_c'].flatten()
	B4_indices_r = indices['B4_indices_r'].flatten()

	M = np.delete(M, delR, axis=0)
	M = np.delete(M, delC, axis=1)

	M = np.delete(M, NA_indices_r, axis=0)
	M = np.delete(M, NA_indices_c, axis=1)

	M = np.delete(M, B4_indices_r, axis=0)

	return M

"""Set delta to avoid dividing by zero"""
def contactProbabilities(M,delta=1e-10):
	coeff = np.nan_to_num(1 / (M+delta))
	PM = np.power(1/np.exp(1),coeff)

	return PM

def RandomSample(data):
    N = len(data)
    return data[np.random.randint(N)]

def bootstrap(data,labels,samplesPerClass=None):
    Nsamples = samplesPerClass
    classes = np.unique(labels)
    
    maxSamples = np.max(np.bincount(labels))

    if samplesPerClass is None or samplesPerClass < maxSamples:
        Nsamples = maxSamples
        
    bootstrapSamples = []
    bootstrapClasses = []
        
    for i, c in enumerate(classes):
        classLabel = c
        classData = data[labels == c]
        
        nBootstrap = Nsamples
        
        for n in range(nBootstrap):
            sample = RandomSample(classData)

            bootstrapSamples.append(sample)
            bootstrapClasses.append(c)
    
    bootstrapSamples = np.asarray(bootstrapSamples)
    bootstrapClasses = np.asarray(bootstrapClasses)
    
    bootstrapData = np.hstack((bootstrapSamples,np.array([bootstrapClasses]).T))
    np.random.shuffle(bootstrapData)
    
    return (bootstrapData[:,:-1], bootstrapData[:,-1])