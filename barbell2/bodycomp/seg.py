import os
import json
import zipfile
import logging

logger = logging.getLogger(__name__)


class MuscleFatSegmentator:

    ARGMAX = 0
    PROBABILITIES = 1

    def __init__(self):
        self.input_files = None
        self.image_dimensions = None
        self.model_files = None
        self.mode = MuscleFatSegmentator.ARGMAX
        self.output_segmentation_files = None

    def load_model(file_path):
        import tensorflow as tf
        file_name = os.path.split(file_path)[1]
        model_directory = os.path.abspath(os.path.curdir + f'/{file_name[:-4]}')
        with zipfile.ZipFile(file_path) as zip_obj:
            zip_obj.extractall(path=model_directory)
        return tf.keras.models.load_model(model_directory, compile=False)

    def load_params(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def load_model_files(self):
        model, contour_model, params = None, None, None
        for file_path in self.model_files:
            file_name = os.path.split(file_path)[1]
            if file_name == 'model.zip':
                model = self.load_model(file_path)
            elif file_name == 'contour_model.zip':
                contour_model = self.load_model(file_path)
            elif file_name == 'params.json':
                params = self.load_params(file_path)
            else:
                logger.error(f'Unknown model file {file_name}')
        return model, contour_model, params

    def execute(self):
        if self.input_files is None:
            logger.error('Input files not specified')
            return None
        if self.image_dimensions is None:
            logger.error('Image dimensions not specified')
            return None
        if self.model_files is None:
            logger.error('Model files not specified')
            return None
        model, contour_model, params = self.load_model_files()


if __name__ == '__main__':
    def main():
        segmentator = MuscleFatSegmentator()
        segmentator.input_files = ['/Users/ralph/Desktop/SliceSelector/L3.dcm']
        segmentator.image_dimensions = (512, 512)
        segmentator.model_files = []
        segmentator.mode = MuscleFatSegmentator.ARGMAX
        files = segmentator.execute()
        for f in files:
            print(f)
    main()
