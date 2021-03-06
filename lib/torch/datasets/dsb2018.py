import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

from lib.tiles import ImageSlicer
from lib.torch.common import find_in_dir, ImageMaskDataset, read_rgb, read_gray, RawDataset
from lib import augmentations as aug


def DSB2018(dataset_dir, grayscale, patch_size):
    """
    Returns train & test dataset or DSB2018
    :param dataset_dir:
    :param grayscale:
    :param patch_size:
    :return:
    """

    images = find_in_dir(os.path.join(dataset_dir, 'images'))
    masks = find_in_dir(os.path.join(dataset_dir, 'masks'))

    x_train, x_test, y_train, y_test = train_test_split(images, masks, random_state=1234, test_size=0.1)

    train_transform = aug.Sequential([
        aug.RandomCrop(patch_size),
        # aug.ImageOnly(aug.RandomGrayscale()),
        # aug.ImageOnly(aug.RandomInvert()),
        aug.ImageOnly(aug.NormalizeImage()),
        # aug.ImageOnly(aug.RandomBrightness()),
        # aug.ImageOnly(aug.RandomContrast()),
        # aug.RandomRotate90(),
        # aug.VerticalFlip(),
        # aug.HorizontalFlip(),
        # aug.ShiftScaleRotate(),
        aug.MaskOnly(aug.MakeBinary()),
        aug.ToTensors()
    ])

    test_transform = aug.Sequential([
        aug.CenterCrop(patch_size, patch_size),
        # aug.ImageOnly(aug.RandomGrayscale(1.0 if grayscale else 0.0)),
        aug.ImageOnly(aug.NormalizeImage()),
        aug.MaskOnly(aug.MakeBinary()),
        aug.ToTensors()
    ])

    train = ImageMaskDataset(x_train, y_train, image_loader=read_rgb, target_loader=read_gray, transform=train_transform, load_in_ram=False)
    test = ImageMaskDataset(x_test, y_test, image_loader=read_rgb, target_loader=read_gray, transform=test_transform, load_in_ram=False)
    num_classes = 1
    return train, test, num_classes


def DSB2018Sliced(dataset_dir, grayscale, patch_size):
    """
    Returns train & test dataset or DSB2018
    :param dataset_dir:
    :param grayscale:
    :param patch_size:
    :return:
    """

    images = [read_rgb(x) for x in find_in_dir(os.path.join(dataset_dir, 'images'))]
    masks = [read_gray(x) for x in find_in_dir(os.path.join(dataset_dir, 'masks'))]

    image_ids = []
    patch_images = []
    patch_masks = []

    for image_id, (image, mask) in enumerate(zip(images, masks)):
        slicer = ImageSlicer(image.shape, patch_size, patch_size // 2)

        patch_images.extend(slicer.split(image))
        patch_masks.extend(slicer.split(mask))
        image_ids.extend([image_id] * len(slicer.crops))

    x_train, x_test, y_train, y_test = train_test_split(patch_images, patch_masks, random_state=1234, test_size=0.1, stratify=image_ids)

    train_transform = aug.Sequential([
        # aug.ImageOnly(aug.RandomGrayscale()),
        # aug.ImageOnly(aug.RandomInvert()),
        aug.ImageOnly(aug.NormalizeImage()),
        # aug.ImageOnly(aug.RandomBrightness()),
        # aug.ImageOnly(aug.RandomContrast()),
        aug.RandomRotate90(),
        aug.VerticalFlip(),
        aug.HorizontalFlip(),
        aug.ShiftScaleRotate(rotate_limit=15),
        aug.MaskOnly(aug.MakeBinary()),
        aug.ToTensors()
    ])

    test_transform = aug.Sequential([
        aug.ImageOnly(aug.NormalizeImage()),
        aug.MaskOnly(aug.MakeBinary()),
        aug.ToTensors()
    ])

    train = RawDataset(x_train, y_train, transform=train_transform)
    test = RawDataset(x_test, y_test, transform=test_transform)
    num_classes = 1
    return train, test, num_classes
