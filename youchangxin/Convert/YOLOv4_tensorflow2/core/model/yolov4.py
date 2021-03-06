# -*- coding: utf-8 -*-
import tensorflow as tf
from core.model.modules import Upper_Concate, Merge, SPP, Linear
from core.model.backbone import CSPDarkNet53
from config import cfg

NUM_CLASS = 6 #len(cfg.YOLO.CLASSES)


class YOLOV4(tf.keras.Model):
    def __init__(self):
        super(YOLOV4, self).__init__()
        out_shape = 3 * (5 + NUM_CLASS)
        self.backbone = CSPDarkNet53()
        self.spp = SPP()

        self.upper_m = Upper_Concate(256, 512)
        self.upper_s = Upper_Concate(128, 256)

        self.merge_m = Merge(256, 512)
        self.merge_l = Merge(512, 1024)

        self.linear_s = Linear(256, out_shape)
        self.linear_m = Linear(512, out_shape)
        self.linear_l = Linear(1024, out_shape)

    def call(self, inputs, training=None, mask=None):
        route_small, route_medial, route_large = self.backbone(inputs, training=training)
        route_large = self.spp(route_large, training=training)

        route_medial = self.upper_m(route_medial, route_large, training=training)
        route_small = self.upper_s(route_small, route_medial, training=training)
        yolo_small = self.linear_s(route_small, training=training)

        route_medial = self.merge_m(route_small, route_medial, training=training)
        yolo_medial = self.linear_m(route_medial, training=training)

        route_large = self.merge_l(route_medial, route_large, training=training)
        yolo_large = self.linear_l(route_large, training=training)

        return yolo_small, yolo_medial, yolo_large



