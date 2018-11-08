import os
import numpy as np
import pickle as pkl

from scipy.sparse import coo_matrix, hstack, vstack
from scipy.io import savemat

chromosome_lengths = {
    'chr1' : 249250621,
    'chr2' : 243199373,
    'chr3' : 198022430,
    'chr4' : 191154276,
    'chr5' : 180915260,
    'chr6' : 171115067,
    'chr7' : 159138663,
    'chrX' : 155270560,
    'chr8' : 146364022,
    'chr9' : 141213431,
    'chr10' : 135534747,
    'chr11' : 135006516,
    'chr12' : 133851895,
    'chr13' : 115169878,
    'chr14' : 107349540,
    'chr15' : 102531392,
    'chr16' : 90354753,
    'chr17' : 81195210,
    'chr18' : 78077248,
    'chr20' : 63025520,
    'chrY' : 59373566,
    'chr19' : 59128983,
    'chr22' : 51304566,
    'chr21' : 48129895
}

def construct(hic_dir='.',prefix='hic',hic_res=100000, verbose=False):
	fullSM = None

	"""Span chrms 1, 3, 5, 7... 21"""
	for i in range(1,23,2):

		# sparse matrix
		rowSM = None

		try:
			"""Interactions with even chromosomes"""
			for j in range(2,23,2):

				if verbose:
					print('Compiling interactions between chr{0} and chr{1}...'.format(i,j))

				filepath = os.path.join(hic_dir, '{2}_chrm{0}_chrm{1}.txt'.format(i,j,prefix))

				file = open(filepath,'r')

				txt_data = np.loadtxt(file)

				nrow = int(chromosome_lengths['chr' + str(i)] / hic_res + 1)
				ncol = int(chromosome_lengths['chr' + str(j)] / hic_res + 1)

				rows = txt_data[:,0] / hic_res
				cols = txt_data[:,1] / hic_res

				if i > j:
					rows = txt_data[:,1] / hic_res
					cols = txt_data[:,0] / hic_res

				data = txt_data[:,2]

				rows = rows.astype(int)
				cols = cols.astype(int)

				SM = coo_matrix((data,(rows, cols)), shape=(nrow, ncol))

				if rowSM is None:
					rowSM = SM
				else:
					rowSM = hstack([rowSM, SM])

			if fullSM is None:
				fullSM = rowSM
			else:
				fullSM = vstack([fullSM, rowSM])
		except IndexError:
			print('Missing data for chr{0}. Omitting...'.format(i))

	return fullSM.toarray()
