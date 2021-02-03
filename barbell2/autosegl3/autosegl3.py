import json


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
