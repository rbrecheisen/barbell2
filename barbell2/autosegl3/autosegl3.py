import json


"""
The AutoSegL3 tool allows a data manager to train a deep learning model that automatically segments
muscle and fat tissue in CT images taken at the 3rd vertebral (L3) level. To train the deep learning model
the tool needs a collection of L3 images and corresponding TAG files that contain the labels of each tissue
to be segmented. To run the trained model on previously unseen CT images the tool only needs a collection of
L3 images. The tool will then produce a mask for each L3 image that outlines the location of the muscle and
fat regions.

For training, if default parameters are used, all the data manager has to do is point the tool to a directory 
containing L3 images and corresponding TAG files. 

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

# {
# 	"image_shape": [512, 512, 1],
# 	"patch_shape": [512, 512, 1],
# 	"data_path_train": "/mnt/localscratch/maastro/Ralph/bodycomposition/training.h5",
# 	"data_path_val": "/mnt/localscratch/maastro/Ralph/bodycomposition/validation.h5",
# 	"data_path_test": "/mnt/localscratch/maastro/Ralph/bodycomposition/testing.h5",
#
# 	"patch_path": "/mnt/localscratch/maastro/Ralph/bodycomposition/training_samples",
# 	"val_patch_path": "/mnt/localscratch/maastro/Ralph/bodycomposition/validation_samples",
# 	"log_path": "/mnt/localscratch/maastro/Ralph/bodycomposition/logs",
# 	"split": 20,
# 	"number_of_patches": 15,
# 	"number_of_augmentations": 2,
# 	"switch_views": "False",
# 	"translate": "False",
#
# 	"min_bound": -200,
# 	"max_bound": 200,
# 	"num_classes": 4,
# 	"batch_size": 1,
# 	"num_steps": 100000,
# 	"train_eval_step": 100,
# 	"val_eval_step": 100,
# 	"save_model_step": 10000,
#
# 	"learning_rate": 0.001,
# 	"decay_steps": 2500,
# 	"decay_rate": 0.5,
# 	"opt_momentum": 0.9,
# 	"dropout_rate": 0.05,
# 	"l2_loss": 0.001
#
# }


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
                'log_path': '.',
                'number_of_patches': 15,
                'number_of_augmentations': 2,
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
        """
        Usage: Train model on training data in <dir_path>. Training data should consist of pairs of L3 images with
        corresponding TAG files containing the labels. Upon loading the images a number of quality checks
        should be performed such as:

            - Checking for consistent dimensions
            - Matching image/TAG files
            - Normalized (original) Hounsfield unit data

        :param dir_path: Directory path to CT images and TAG files.
        """
        pass

    def predict(self, file_or_dir_path):
        """
        Usage: predicts labels for given CT image (file) or directory of CT images (directory)
        :param file_or_dir_path: File or directory to CT image(s)
        """
        pass


def main():
    AutoSegL3()


if __name__ == '__main__':
    main()
