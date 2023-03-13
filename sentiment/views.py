from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.models import User
from chat.models import Room, RoomUsers, Message
from chat.serializers import RoomUsersSerializer
import tensorflow as tf
import numpy as np
from transformers import DistilBertTokenizer, TFDistilBertModel
import string
import os
from django.conf import settings

@api_view(['PUT'])
def get_sentiment(request):
    if request.method == 'PUT':
        # Gets name, review and room from frontend
        email = request.data['email']
        slug = request.data['slug']
        message = request.data['message']

        # Gets user
        user = User.objects.get(email=email)

        # Gets room
        room = Room.objects.get(slug=slug)

        # Gets messages in room
        room_messages = Message.objects.filter(room=room.id)

        # Gets messages of a user in a particular room
        user_messages = room_messages.filter(author=user.id)

        # Combines previous messages and review
        text = message
        print("First: ", text)

        for user_message in user_messages:
            text += ' ' + user_message.message

        print("Second: ", text)
        # The 'text' is made into a suitable format
        text = text.translate(str.maketrans('', '', string.punctuation)) # Removes punctuation
        print("Third: ", text)
        text = text.lower()
        print("Fourth (this is final): ", text)

        # Initialises and loads distilbert model
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        model = TFDistilBertModel.from_pretrained("distilbert-base-uncased")

        input_ids = tf.keras.layers.Input(shape=(256,), name="input_ids", dtype=tf.int32)
        attn_mask = tf.keras.layers.Input(shape=(256,), name="attention_mask", dtype=tf.int32)

        embds = model(input_ids, attention_mask=attn_mask)[0] # Attention mask tells what input tokens the model should be trained on (e.g. padding tokens would be 0 as they shouldn't be used for training)
        out = tf.keras.layers.GlobalMaxPool1D()(embds)
        out = tf.keras.layers.Dense(128, activation="relu")(out)
        out = tf.keras.layers.Dropout(0.1)(out)
        out = tf.keras.layers.Dense(32, activation="relu")(out)
        y = tf.keras.layers.Dense(6, activation="sigmoid")(out)

        sentiment_model = tf.keras.Model(inputs=[input_ids, attn_mask], outputs=y)
        sentiment_model.layers[2].trainable = True

        optim = tf.keras.optimizers.Adam(learning_rate=5e-05, epsilon=1e-08, weight_decay=0.01)
        loss_func = tf.keras.losses.CategoricalCrossentropy()
        acc = tf.keras.metrics.CategoricalAccuracy('accuracy')
        
        sentiment_model.compile(optimizer=optim, loss=loss_func, metrics=[acc])

        file_model = os.path.join(settings.BASE_DIR, 'sentiment/models/my_model_weights.h5')
        sentiment_model.load_weights(file_model)

        tokenized_predict = tokenizer(
            text = text,
            add_special_tokens = True, # For [101] and [102] paddings
            max_length = 256,
            truncation = True, # For uniform length
            padding = 'max_length', # [0] for padding
            return_tensors = 'tf',
            return_attention_mask = True 
        )

        # Returns array of sentiments => [['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']]
        prediction = sentiment_model.predict({'input_ids':tokenized_predict['input_ids'],'attention_mask':tokenized_predict['attention_mask']})

        # Gets max value in array
        sentiment = np.argmax(prediction)

        # Gets correct emotion from sentiment array position
        emotion = ''

        if (sentiment == 0):
            emotion = 'Anger'
        elif (sentiment == 1):
            emotion = 'Fear'
        elif (sentiment == 2):
            emotion = 'Happy'
        elif (sentiment == 3):
            emotion = 'Love'
        elif (sentiment == 4):
            emotion = 'Sadness'
        elif (sentiment == 5):
            emotion = 'Surprise'
        else:
            print('Something went wrong!')

        
        # Gets RoomUser from db
        room_user = RoomUsers.objects.filter(user=user).get(room=room)

        # Updates db value
        serializer = RoomUsersSerializer(room_user, data={'room': room.id,'user': user.id,'sentiment': emotion})

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)
    

def remove_punctuation(line):
    line = line.translate(str.maketrans('', '', string.punctuation))
    return line
