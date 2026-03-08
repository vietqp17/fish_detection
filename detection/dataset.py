import torch
from torch.utils.data import Dataset
import cv2
import os


class FishDataset(Dataset):

    def __init__(self, image_dir, annotations, transforms=None):
        self.image_dir = image_dir
        self.annotations = annotations
        self.transforms = transforms
        self.images = list(annotations.keys())

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_name = self.images[idx]
        img_path = os.path.join(self.image_dir, img_name)

        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = self.annotations[img_name]["boxes"]
        labels = self.annotations[img_name]["labels"]

        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32),
            "labels": torch.tensor(labels, dtype=torch.int64)
        }

        image = torch.tensor(image, dtype=torch.float32).permute(2, 0,
                                                                 1) / 255.0

        return image, target
