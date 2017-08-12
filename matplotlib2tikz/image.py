# -*- coding: utf-8 -*-
#
import os

import matplotlib as mpl
import numpy
from six import BytesIO, string_types
try:
    from base64 import encodebytes
except ImportError:
    from base64 import encodestring as encodebytes


def draw_image(data, obj):
    '''Returns the PGFPlots code for an image environment.
    '''
    content = []

    if not data['embed_images']:
        if 'img number' not in data.keys():
            data['img number'] = 0

        # Make sure not to overwrite anything.
        file_exists = True
        while file_exists:
            data['img number'] = data['img number'] + 1
            filename_or_handle = os.path.join(
                data['output dir'],
                data['base name'] + str(data['img number']) + '.png'
            )
            file_exists = os.path.isfile(filename_or_handle)
    else:
        filename_or_handle = BytesIO()

    # store the image as in a file
    img_array = obj.get_array()

    dims = img_array.shape

    if len(dims) == 2:  # the values are given as real numbers: convert using cmap
        image = obj.get_cmap()(obj.norm(img_array))
    else:
        assert len(dims) == 3 and dims[2] in [3, 4]
        image = img_array

    if obj.origin == "lower":
        image = numpy.flipud(img_array)

    mpl.pyplot.imsave(fname=filename_or_handle, arr=image)

    # write the corresponding information to the TikZ file
    extent = obj.get_extent()

    # the format specification will only accept tuples
    if not isinstance(extent, tuple):
        extent = tuple(extent)

    # Explicitly use \pgfimage as includegrapics command, as the default
    # \includegraphics fails unexpectedly in some cases

    if not data['embed_images']:
        rel_filepath = os.path.basename(filename_or_handle)
        if data['rel data path']:
            rel_filepath = os.path.join(data['rel data path'], rel_filepath)

        graphic_embedding_command = '\\pgfimage'
        graphic_embedding_parameter = rel_filepath
    else:
        graphic_embedding_command = '\\pgfimageembedded'
        graphic_embedding_parameter = encodebytes(filename_or_handle.getbuffer())
        if not isinstance(graphic_embedding_parameter, string_types):
            graphic_embedding_parameter = '%\n' + graphic_embedding_parameter.decode()

    content.append(
            '\\addplot graphics [includegraphics cmd=%s,'
            'xmin=%.15g, xmax=%.15g, '
            'ymin=%.15g, ymax=%.15g] {%s};\n'
            % ((graphic_embedding_command,) + extent + (graphic_embedding_parameter,))
            )

    return data, content
