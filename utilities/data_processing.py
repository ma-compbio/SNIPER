import os
import numpy as np

from subprocess import call
from scipy.io import loadmat, savemat

def chrom_sizes(f,length=np.inf):
    data = open(f,'r')
    
    sizes = {}
    
    for line in data:
        ldata = line.split()
        
        if len(ldata[0]) > length:
            continue
            
        sizes[ldata[0]] = int(ldata[1])

    return sizes

from utilities.interchromosome_matrix import construct

def constructAndSave(tmp_dir,prefix):
	M = construct(tmp_dir, prefix=prefix)

	savemat(os.path.join(tmp_dir,'%s_matrix.mat' % prefix),{'inter_matrix' : M})

	return M

def hicToMat(h,juicer_path,tmp_dir='.',prefix='hic',autoremove=False,overwrite=False,save_matrix=False,verbose=False):
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

			cmd = 'java -jar {0} dump observed KR {1} {2} {3} BP 100000 {4} > tmp_juicer_log'.format(juicer_path,h,chrm1,chrm2,output_path)
			call([cmd],shell=True)

	""" File path of the inter-chromosomal matrix """
	M_filepath = os.path.join(tmp_dir,'%s_matrix.mat' % prefix)

	""" If overwrite flag is set, reconstruct matrix and check save flag """
	if overwrite:
		M = constructAndSave(tmp_dir,prefix)
	else:
		""" If overwrite unset, check if filepath exists and either load mat or construct new """
		if os.path.isfile(M_filepath):
			M = loadmat(M_filepath)['inter_matrix']
		else:
			M = constructAndSave(tmp_dir,prefix)

	""" If autoremove is set, remove hic .txt files """
	if autoremove:
		for chrm1 in range(1,23,2):
			for chrm2 in range(2,23,2):
				file_path = os.path.join(tmp_dir,'{2}_chrm{0}_chrm{1}.txt'.format(chrm1,chrm2,prefix))
				try:
					os.remove(file_path)
				except:
					continue
	return M

""" Trims sparse, NA, and B4 regions """
def trimMat(M,indices):
	row_indices = indices['odd_indices'].flatten()
	col_indices = indices['even_indices'].flatten()

	M = M[row_indices,:]
	M = M[:,col_indices]

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

def Sigmoid(data):
    return 1 / (1 + np.exp(-data))

def getColorString(n):
    subcColors = ['34,139,34','152,251,152','220,20,60','255,255,0','112,128,144']
    return subcColors[n]

def getSubcName(n):
    order = ['A1','A2','B1','B2','B3']
    return order[n]

def predictionsToBed(path, odds, evens, cropMap, res=100000, sizes_file='data/hg38.chrom.sizes'):
	rowMap = cropMap['rowMap'].astype(np.int)
	colMap = cropMap['colMap'].astype(np.int)

	sizes = chrom_sizes(sizes_file)

	file = open(path,'w')

	for i,p in enumerate(np.argmax(odds,axis=1)):
		m = rowMap
		chrm, start = 'chr'+str(m[i,1]), m[i,2] * res
		end = np.min([start + res, sizes[chrm]])
		line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(chrm, start, end, getSubcName(p), 0, '.' , start, end, getColorString(p))
		file.write(line)

	for i,p in enumerate(np.argmax(evens,axis=1)):
		m = colMap
		chrm, start = 'chr'+str(m[i,1]), m[i,2] * res
		end = np.min([start + res, sizes[chrm]])
		line = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(chrm, start, end, getSubcName(p), 0, '.' , start, end, getColorString(p))
		file.write(line)

	file.close()