import os

from barbell2 import CreateHDF5
from barbell2 import AutoSegL3CNN


"""
The AutoSegL3 tool allows a data manager to train a deep learning model that automatically segments
muscle and fat tissue in CT images taken at the 3rd vertebral (L3) level. To train the deep learning model
the tool needs a collection of L3 images and corresponding TAG files that contain the labels of each tissue
to be segmented. To run the trained model on previously unseen CT images the tool only needs a collection of
L3 images. The tool will then produce a mask for each L3 image that outlines the location of the muscle and
fat regions.

For training, if default parameters are used, all the data manager has to do is point the tool to a directory 
containing L3 images and corresponding TAG files. From this directory, an HDF5 file will be generated. During
this process the images and TAG files will be checked for certain characteristics like a common dimension of
512 by 512 pixels, pixels containing normalized Hounsfield units, etc. Any images that do pass this initial 
quality check will be reported in a text file. 

For testing the training procedure, the tool also has to be pointed to a directory containing both L3 images 
and TAG files. However, only the L3 images will be used for generating segmentations. The TAG files will be used 
to evaluate the quality of the segmentations. This step will also produce a summary report containing some 
performance metrics, e.g., Dice scores. Note that the testing phase is only meant to obtain realistic performance
metrics. To use the model for prediction, train it on all data you have (see next section).

For model preparation, train it on all data you have. Generate a CSV database containing certain clinical scores 
for each L3 image, e.g., SMRA, muscle index, SAT index and VAT index (what other scores can we think of?). This 
database can then be used to visualize the spread of scores across all images in the training data. When a new
image is predicted you can also highlight its position within the spread of the training scores.  

For prediction, the tool has to be pointed to a directory containing only L3 images. 
"""


class AutoSegL3:

    def __init__(self, params):
        super(AutoSegL3, self).__init__()
        self.params = params

    @staticmethod
    def get_output_files(output_dir, test_size):
        output_files = list()
        output_files.append(os.path.join(output_dir, 'training.h5'))
        if test_size > 0.0:
            output_files.append(os.path.join(output_dir, 'test.h5'))
        return output_files

    def train(self, dir_path):
        output_dir = self.params['output_dir']
        os.makedirs(output_dir, exist_ok=True)
        output_files = self.get_output_files(output_dir, self.params['test_size'])
        creator = CreateHDF5(
            dir_path=dir_path,
            output_files=output_files,
            rows=self.params['image_shape'][0],
            columns=self.params['image_shape'][1],
            test_size=self.params['test_size'],
            is_training=True,
            log_dir=self.params['log_dir'],
        )
        training_file, test_file = creator.create_hdf5()
        network = AutoSegL3CNN(training_file, test_file, self.params)
        network.run()

    def predict(self, file_or_dir_path):
        pass


def main():
    pass


if __name__ == '__main__':
    main()
