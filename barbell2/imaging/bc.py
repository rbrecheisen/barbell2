import os
import pydicom
import numpy as np


class BodyCompositionCalculator2D:

    def __init__(self, image, mask):
        self.image = pydicom.dcmread(image)
        self.image = self.image.pixel_array
        self.mask = np.load(mask)

    @staticmethod
    def calculate_area(mask, label, pixel_spacing):
        pass

    @staticmethod
    def calculate_mean_pixel_value(image, mask, label):
        pass

    def execute():
        pass


if __name__ == '__main__':
    def main():
        pass
    main()
