# Create labels base on clean mask and optionally, multiple ROIs
import cv2, os
import numpy as np
from skimage.measure import label
from skimage.color import label2rgb
from plantcv.plantcv import params, roi_objects, Objects, warn
from plantcv.plantcv._debug import _debug
from plantcv.plantcv._helpers import _roi_filter
from plantcv.plantcv._helpers import _cv2_findcontours






def create_labels(mask, rois, roi_type="partial"):
    """Create a labeled mask where connected regions of non-zero pixels are assigned
    a label value based on the provided region of interest (ROI)

    If the order of labels is not important `roi_type='auto'` and `rois=None` can
    be used to automatically assign the labels

    Inputs:
    mask            = mask image
    rois            = list of multiple ROIs (from roi.multi or roi.auto_grid)
    roi_type        = 'cutto', 'partial' (for partially inside, default), 'largest' (keep only the largest contour), or 'auto' (use the mask alone withtout roi filtering)

    Returns:
    mask            = Labeled mask
    num_labels      = Number of labeled objects

    :param mask: numpy.ndarray
    :param rois: plantcv.plantcv.classes.Objects
    :return labeled_mask: numpy.ndarray
    :return num_labels: int
    """

    # Store debug mode
    debug = params.debug
    params.debug = None

    # Auto logic for when the order of labels is not important
    if roi_type.upper() == "AUTO":
        if rois is not None:
            warn("When using roi_type='auto' the rois parameter is ignored")

        # label will work with any number of objects in the mask
        labeled_mask, num_labels = label(mask, background=0, return_num=True, connectivity=2)

    # use the rois for labeling
    else:
        contours, hierarchy = _cv2_findcontours(mask)
        labeled_mask = np.zeros(mask.shape[:2], dtype=np.int32)
        for i, roi in enumerate(rois):
            kept_cnt, kept_hierarchy, mask = _roi_filter(img=mask, roi=roi, obj=contours,
                                                hierarchy=hierarchy, roi_type=roi_type)

            # Pixel intensity of (i+1) such that the first object has value
            cv2.drawContours(labeled_mask, kept_cnt, -1, (i+1), -1)
            num_labels = np.unique(labeled_mask).size -1

    # Restore debug parameter
    params.debug = debug
    colorful = label2rgb(labeled_mask)
    colorful2 = ((255*colorful).astype(np.uint8))

    _debug(colorful2, filename=os.path.join(params.debug_outdir, str(params.device) + '_label_colored_mask.png'))

    return labeled_mask, num_labels
