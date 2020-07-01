from im2mesh import config, data, common
from torch import nn
from torchvision import transforms
from torchvision import models

from im2mesh.encoder.depth_conv import Depth_Resnet18

class DepthClassify_Resnet18(nn.Module):
    def __init__(self, num_classes=13, c_dim=512):
        super(DepthClassify_Resnet18, self).__init__()
        self.features = Depth_Resnet18(c_dim = c_dim, use_linear=True)
        self.pred_fc = nn.Linear(c_dim, num_classes)
        self.loss_func = nn.CrossEntropyLoss()

    def forward(self, data, device):
        gt_depth_maps = data.get('inputs.depth').to(device)
        gt_mask = data.get('inputs.mask').to(device).byte()
        gt_depth_maps[1. - gt_mask] = 0.
        out = self.features(gt_depth_maps)
        out = self.pred_fc(out)
        return out

    def get_loss(self, data, device):
        class_gt = data.get('category').to(device)

        out = self.forward(data, device)
        loss = self.loss_func(out, class_gt)
        return loss

    
    def to(self, device):
        model = super().to(device)
        model._device = device
        return model