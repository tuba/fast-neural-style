__author__ = 'alexander'

import tensorflow as tf

x = tf.Variable(3, name='x')
y = tf.Variable(4, name='y')
z = x + y

with tf.Session() as sess:
    sess.run(tf.initialize_all_variables())
    result = sess.run(z)
    print(result)
