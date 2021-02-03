import json


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

    def __init__(self, params=None):

        super(AutoSegL3, self).__init__()

        if params is not None:
            with open(params, 'r') as f:
                self.params = json.load(f)
        else:
            self.params = {
                'image_shape': (512, 512, 1),
                'patch_shape': (512, 512, 1),
                'output_path': '/tmp/autosegl3',
                'number_of_patches': 15,
                'number_of_augmentations': 2,
                'switch_views': False,
                'translate': False,
                'min_bound': -200,
                'max_bound': 200,
                'batch_size': 1,
                'num_steps': 100000,
                'train_eval_step': 100,
                'validation_eval_step': 100,
                'save_model_step': 10000,
                'learning_rate': 0.001,
                'decay_steps': 2500,
                'decay_rate': 0.5,
                'opt_momentum': 0.9,
                'dropout_rate': 0.05,
                'l2_loss': 0.001,
            }

    def train(self, dir_path):
        pass

    def predict(self, file_or_dir_path):
        pass


def main():
    AutoSegL3()


if __name__ == '__main__':
    main()
