from io import BytesIO
import os
from PIL import Image, ImageDraw
import requests

from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import FaceAttributeType
from msrest.authentication import CognitiveServicesCredentials



KEY = '7e7ad022955a4fddbd11bdadfb567c9b'

ENDPOINT = 'https://wally.cognitiveservices.azure.com/'

face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))



face1_url = 'https://auth.etna-alternance.net/api/users/lequer_r/photo'
face1_name = os.path.basename(face1_url)
face2_url = 'https://auth.etna-alternance.net/api/users/carra_c/photo'
face2_name = os.path.basename(face2_url)


url_images = [face1_url, face2_url]


face_attributes = ['age', 'gender', 'headPose', 'smile', 'facialHair', 'glasses', 'emotion']


for image in url_images:
    detected_faces = face_client.face.detect_with_url(url=image, return_face_attributes=face_attributes)
    if not detected_faces:
        raise Exception(
            'No face detected from image {}'.format(os.path.basename(image)))

    
    for face in detected_faces:
        print()
        print('Detected face ID from', os.path.basename(image), ':')
        
        print(face.face_id)
        
        print()
        print('Facial attributes detected:')
        print('Age: ', face.face_attributes.age)
        print('Gender: ', face.face_attributes.gender)
        print('Head pose: ', face.face_attributes.head_pose)
        print('Smile: ', face.face_attributes.smile)
        print('Facial hair: ', face.face_attributes.facial_hair)
        print('Glasses: ', face.face_attributes.glasses)
        print('Emotion: ')
        print('\tAnger: ', face.face_attributes.emotion.anger)
        print('\tContempt: ', face.face_attributes.emotion.contempt)
        print('\tDisgust: ', face.face_attributes.emotion.disgust)
        print('\tFear: ', face.face_attributes.emotion.fear)
        print('\tHappiness: ', face.face_attributes.emotion.happiness)
        print('\tNeutral: ', face.face_attributes.emotion.neutral)
        print('\tSadness: ', face.face_attributes.emotion.sadness)
        print('\tSurprise: ', face.face_attributes.emotion.surprise)
        print()

    
    def getRectangle(faceDictionary):
        rect = faceDictionary.face_rectangle
        left = rect.left
        top = rect.top
        right = left + rect.width
        bottom = top + rect.height

        return ((left, top), (right, bottom))

    
    response = requests.get(image)
    img = Image.open(BytesIO(response.content))

    
    print('Drawing rectangle around face... see popup for results.')
    print()
    draw = ImageDraw.Draw(img)
    for face in detected_faces:
        draw.rectangle(getRectangle(face), outline='red')

    
    img.show()