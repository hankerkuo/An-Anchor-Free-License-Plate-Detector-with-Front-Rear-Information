import numpy as np
import imgaug.augmenters as iaa
import cv2

from img_utility import read_img_from_dir
from dataset_utility import CCPD_FR_vertices_info, CCPD_FR_front_rear_info
from dataset_utility import vernex_vertices_info, vernex_front_rear_info, vernex_fr_class_info
from drawing_utility import draw_LP_by_vertices
from config import Configs


def data_aug(img_paths):
    c = Configs()

    sometimes = lambda aug: iaa.Sometimes(0.5, aug)
    imgs = []
    key_pts = []
    fr_classes = []

    for img_path in img_paths:
        img = cv2.imread(img_path)
        cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgs.append(img)

        if c.dataset_code in ['CCPD_FR']:
            vertices_info = CCPD_FR_vertices_info
            front_rear_info = CCPD_FR_front_rear_info
        elif c.dataset_code in ['vernex']:
            vertices_info = vernex_vertices_info
            front_rear_info = vernex_front_rear_info
            fr_classes.append(vernex_fr_class_info(img_path))

        if c.model_code in ['Hourglass+Vernex_lp', 'Hourglass+WPOD', 'WPOD+WPOD']:
            vertices = np.array(vertices_info(img_path))
        elif c.model_code in ['Hourglass+Vernex_lpfr', 'WPOD+vernex_lpfr']:
            vertices = np.array(vertices_info(img_path) + front_rear_info(img_path))

        key_pts.append(vertices)

    seq = iaa.Sequential([
                        sometimes(iaa.Affine(scale={"x": (0.5, 1), "y": (0.5, 1)}, shear=(-60, 60), rotate=(-25, 25), cval=255)),
                        sometimes(iaa.PerspectiveTransform(scale=(0.05, 0.1), keep_size=False, cval=255)),
                        iaa.AddToHueAndSaturation(value=(-50, 50)),
                        iaa.Fliplr(0.5),
                        iaa.Affine(scale=(0.2, 1), cval=255)
                                                   ], random_order=True)
    '''
    seq = iaa.Sequential([iaa.Fliplr(0.5)])
    '''

    imgs_aug, vertices_aug = seq(images=imgs, keypoints=key_pts)

    for img_aug in imgs_aug:
        cv2.cvtColor(img_aug, cv2.COLOR_RGB2BGR)

    return imgs_aug, vertices_aug, fr_classes


if __name__ == '__main__':
    from os.path import join
    from collections import deque
    # img_paths = deque(read_img_from_dir('/home/shaoheng/Documents/Thesis_KSH/training_data/vernex'))
    img_paths = '/home/shaoheng/Documents/Thesis_KSH/training_data/vernex/717&482_527&482_527&421_717&421_958&555_255&555_255&186_958&186_front.jpg'
    out_dir = '/home/shaoheng/Documents/thesis_ingredient/aug_single_data_several_times'
    n = 100
    for _ in range(100):
        imgs_to_aug = [img_paths]

        images_aug, keypoints_aug, fr_classes = data_aug(imgs_to_aug)
        for image_aug, keypoint_aug, fr_class in zip(images_aug, keypoints_aug, fr_classes):
            image_aug = draw_LP_by_vertices(image_aug, keypoint_aug[0:4])
            image_aug = draw_LP_by_vertices(image_aug, keypoint_aug[4:8], (36, 247, 255))
            print (fr_class)

            n += 1
            cv2.imwrite(join(out_dir, '%d.jpg' % n), image_aug)
            # cv2.imshow('img', image_aug)
            # cv2.waitKey(0)


