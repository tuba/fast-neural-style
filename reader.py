from os import listdir
from os.path import isfile, join
import tensorflow as tf

mean_pixel = [123.68, 116.779, 103.939]  # ImageNet average from VGG ..


def preprocess(image, size, max_length):
    shape = tf.shape(image)
    size_t = tf.constant(size, tf.float64)
    height = tf.cast(shape[0], tf.float64)
    width = tf.cast(shape[1], tf.float64)

    cond_op = tf.less(width, height) if max_length else tf.less(height, width)

    new_height, new_width = tf.cond(
        cond_op,
        lambda: (size_t, (width * size_t) / height),
        lambda: ((height * size_t) / width, size_t))

    resized_image = tf.image.resize_images(image, tf.to_int32(new_height), tf.to_int32(new_width))
    normalised_image = resized_image - mean_pixel
    return normalised_image


# max_length: Wether size dictates longest or shortest side. Default longest
def get_image(path, size, max_length=True):
    png = path.lower().endswith('png')
    img_bytes = tf.read_file(path)

    if png:
        image = tf.image.decode_png(img_bytes, channels=3)
    else:
        image = tf.image.decode_jpeg(img_bytes, channels=3)

    return preprocess(image, size, max_length)


def isPng(path):
    filenames = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    return filenames[0].lower().endswith('png')


def image(n, size, path, epochs=2, shuffle=True, crop=True):
    images = tf.train.match_filenames_once(path + '/*')
    # WTF? why string producer need epoch numbers?
    filename_queue = tf.train.string_input_producer(images, num_epochs=epochs, shuffle=shuffle)
    reader = tf.WholeFileReader()
    _, img_bytes = reader.read(filename_queue)

    if isPng(path):
        image = tf.image.decode_png(img_bytes, channels=3)
    else:
        image = tf.image.decode_jpeg(img_bytes, channels=3)

    processed_image = preprocess(image, size, False)
    if not crop:
        result = tf.train.batch([processed_image], n, dynamic_pad=True)
        return result

    cropped_image = tf.slice(processed_image, [0, 0, 0], [size, size, 3])
    cropped_image.set_shape((size, size, 3))

    images = tf.train.batch([cropped_image], n)
    return images
