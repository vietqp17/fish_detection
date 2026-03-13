import sys
from types import SimpleNamespace

import numpy as np
from PIL import Image
import pytest
import torch
import torchvision


class _LoaderModel:
    """Minimal model stub used while importing the detection module."""

    def __init__(self):
        cls_score = SimpleNamespace(in_features=1024)
        box_predictor = SimpleNamespace(cls_score=cls_score)
        self.roi_heads = SimpleNamespace(box_predictor=box_predictor)

    def to(self, _device):
        return self

    def eval(self):
        return self


class _InferenceModel:

    def __call__(self, _images):
        return [{
            "boxes":
            torch.tensor([[8, 8, 40, 40], [1, 1, 5, 5]], dtype=torch.float32),
            "scores":
            torch.tensor([0.90, 0.20], dtype=torch.float32),
        }]


def _import_detection_module(monkeypatch):

    def fake_fasterrcnn_resnet50_fpn(*_args, **_kwargs):
        return _LoaderModel()

    monkeypatch.setattr(
        torchvision.models.detection,
        "fasterrcnn_resnet50_fpn",
        fake_fasterrcnn_resnet50_fpn,
    )

    sys.modules.pop("app.services.detection", None)
    import app.services.detection as detection  # pylint: disable=import-outside-toplevel

    return detection


def test_detect_fish_filters_and_formats(monkeypatch):

    detection = _import_detection_module(monkeypatch)

    image_path = "/Users/vietpham/Library/CloudStorage/Dropbox/30-downloads/test-fish.jpg"

    monkeypatch.setattr(detection, "model", _InferenceModel())
    result_image, detections = detection.detect_fish(image_path,
                                                     confidence_threshold=0.5)

    assert result_image.size == (64, 64)
    assert len(detections) == 1
    assert detections[0]["id"] == 1
    assert detections[0]["confidence"] == "90.00%"
    assert detections[0]["box"] == [8.0, 8.0, 40.0, 40.0]


def test_detect_fish_raises_for_missing_file(monkeypatch, tmp_path):
    detection = _import_detection_module(monkeypatch)
    missing_path = tmp_path / "missing.png"

    with pytest.raises(Exception):
        detection.detect_fish(str(missing_path))
