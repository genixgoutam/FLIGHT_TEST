# convert_model.py
import tensorflow as tf

model = tf.keras.models.load_model("qaoa_angle_predictor.keras")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("qaoa_angle_predictor.tflite", "wb") as f:
    f.write(tflite_model)