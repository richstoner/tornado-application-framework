import requests
import os
#import numpy as np
import urllib
#import matplotlib.pyplot as plt
from scipy import ndimage
from scipy import misc
from skimage import filter
import json

# queue utilities
from rq import get_current_job
import socket


def processImage(image_path):

    #job = get_current_job()
    #
    #job.meta['handled_by'] = socket.gethostname()
    #job.save()

    im = ndimage.imread(image_path, True)
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


def processDropboxImage(files):

    for file in files:

        import uuid
        url_to_grab = file['link']
        image_path = '/vagrant/app/static/uploads/%s%s' % (uuid.uuid4(), os.path.splitext(file['link'])[1])
        urllib.urlretrieve(url_to_grab,image_path)

        im = ndimage.imread(image_path, True)
        edges2 = filter.canny(im, sigma=3)
        misc.imsave(image_path[:-4] + '-canny.jpg', edges2)

        return_data = {}
        return_data['processed'] = image_path[:-4] + '-canny.jpg'
        return_data['original'] = image_path
        return_data['src'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1]
        return_data['srcproc'] = '/static/uploads/%s' % os.path.split(return_data['original'])[1][:-4] + '-canny.jpg'
        #return_data['callback_id'] = callback_id

        return json.dumps(return_data)




def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())