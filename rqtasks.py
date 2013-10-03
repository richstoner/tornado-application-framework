import requests
import os
#import numpy as np
#import matplotlib.pyplot as plt
from scipy import ndimage
from scipy import misc
from skimage import filter
import json

def processImage(image_path):

    im = ndimage.imread(image_path, True)
    #print im.shape
    edges2 = filter.canny(im, sigma=3)

    misc.imsave(image_path[:-4] + '-canny.jpg', edges2)

    return_data = {}
    return_data['processed'] = image_path[:-4] + '-canny.jpg'
    return_data['original'] = image_path

    return_data['src'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1]
    return_data['srcproc'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1][:-4] + '-canny.jpg'

    #return_data['callback_id'] = callback_id
    return json.dumps(return_data)
    #return 3
    #return image_path[:-4] + '-canny.jpg'

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())