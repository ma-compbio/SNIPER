# README for SNIPER
Please email kxiong@andrew.cmu.edu with any questions about installation or usage.

# Installation

To quickly install SNIPER, clone SNIPER's repository and install the necessary requirements by running

`pip install -r requirements.txt`

in the shell. We recommend creating a separate python 3.6 environment.

## Requirements

All Python dependencies can be installed by running

`pip install -r requirements.txt` (see Installation)

### Python dependencies:

* Python (3.6.5 or 3.6.7). Any version of Python 3.5 or 3.6 should work, but SNIPER has been confirmed to work on 3.6.5 and 3.6.7.
* Tensorflow-GPU (1.12.0)
* h5py (2.8.0)
* Keras (2.2.4)
* numpy (1.15.4)
* scipy (1.11.0)

### Juicer Tools

[Juicer tools](https://github.com/aidenlab/juicer/wiki/Juicer-Tools-Quick-Start) is a utility developed by the Erez Lieberman-Aiden lab that can extract Hi-C data from [.hic files](https://github.com/aidenlab/juicer/wiki/Pre). Follow the link provided to download `juicer_tools.jar`.

`cd` into the directory where `juicer_tools.jar` is installed and run the following to create a symbolic link to `juicer_tools.jar`:

`ln -s juicer_tools.jar juicer_tools`

SNIPER calls `juicer_tools` in lieu of Juicer Tool's direct file path.

### CUDA and cuDNN:

SNIPER uses [CUDA 9.0](https://developer.nvidia.com/cuda-90-download-archive) and [cuDNN](https://developer.nvidia.com/cudnn) v7.0.5 to run Keras on the `tensorflow-gpu` backend. SNIPER should work with recent versions of CUDA and cuDNN as well. Please email kxiong@andrew.cmu.edu with any questions regarding python and CUDA environments.

# Usage

SNIPER is separated into two modules - training and application. To **train** a new SNIPER model, run the following python command:

`python sniper_train.py <input_hic_path> <target_hic_path> <annotation_path> [options]`

`input_hic_path` is the file path to the .hic file of the downsampled training Hi-C matrix. `target_hic_path` is the path to the .hic file of the dense target Hi-C matrix. We have provided GM12878's ground truth annotations in .mat format in SNIPER's root directory. `annotation_path` is the path to a .mat file of the GM12878 annotations published by Rao et al. (2014). We have included a .mat file of their annotations in the root directory of this repository (`labels.mat`).

To **apply** SNIPER to another cell line, run the following python command:

`python sniper.py <input_path> <output_path> <odd_encoder><odd_clf> <even_encoder> <even_clf> [options]`

`input_path` specifies the path to the input Hi-C matrix (.hic or .mat format). `output_path` specifies a .mat file of the output predictions. `[odd/even]_encoder` specifies the keras model of the autoencoder trained with odd or even chromosomes along the rows. `[odd/even]_clf` specifies the keras model of the classifier trained with odd or even chromosomes along the rows.

Pre-computed SNIPER models can be found here:

https://cmu.box.com/s/axbrw67uaixwej4rxeho9eu3hjr5o4hx

## Command line options:

`-c` Specify a custom crop map directory that contains a crop map and crop indices. A crop map maps chromatin loci after the original matrix was trimmed to original chromatin locations before removing sparse loci, loci labeled as NA, and loci labeled as B4. Crop map format:

* N-by-3 2D array where N corresponds to the number of rows in the odd or even training matrices.
* Column 1 - index of a locus along the rows or columns of the input matrix before trimming
* Column 2 - chromosome of a locus
* Column 3 - position within the chromosome in units of 100kb

The row and column crop maps we used are provided in the `crop_map` directory.
Crop indices specify which rows and columns are sparse or labeled as NA or B4 in Rao et al's annotation set, which are removed from the input matrix. The general rule of thumb is to remove rows and columns where more than 30% of entries are zeros.

`-dd` Specifiy a directory to store output files:
* .txt files from juicer_tools if they aren't flagged for automatic removal
* .mat files of Hi-C matrices if the `-sm` flag is set
* Autoencoder, encoder, and classifier keras models
By default, SNIPER will store all files to its installation directory. We recommend setting this flag to avoid clutter in the installation directory and prevent unnecessary drive strain if SNIPER is installed on a solid state drive.

`-sm` Turn this flag on to store .mat files of Hi-C matrices. Doing so will occupy approximately 3.2 GB of disk space but save a substantial amount of time if the pipeline abruptly terminates for some reason and has to be re-run.

`-ar` Turn this flag on to automatically remove .txt files output by Juicer Tool. Doing so will prevent clutter on the hard drive. Leaving this flag off will save time on subsequent training runs. We recommend turning this flag on if running multiple training instances on different cell types in the same directory.

`-ow` Turn this flag on to overwrite data existing on in the `-dd` directory. Recommended if running a new training instance on different cell types in a directory with existing data.