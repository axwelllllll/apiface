import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO

from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from PIL import Image



KEY = "7e7ad022955a4fddbd11bdadfb567c9b"

ENDPOINT = "https://wally.cognitiveservices.azure.com/"

IMAGE_BASE_URL = 'https://csdx.blob.core.windows.net/resources/Face/Images/'

PERSON_GROUP_ID = str(uuid.uuid4())


TARGET_PERSON_GROUP_ID = str(uuid.uuid4())


face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

print('-----------------------------')
print()
print('DETECT FACES')
print()

single_face_image_url = 'https://auth.etna-alternance.net/api/users/lequer_r/photo'
single_image_name = os.path.basename(single_face_image_url)

detected_faces = face_client.face.detect_with_url(url=single_face_image_url, detection_model='detection_03')
if not detected_faces:
	raise Exception('No face detected from image {}'.format(single_image_name))


print('Detected face ID from', single_image_name, ':')
for face in detected_faces: print (face.face_id)
print()

first_image_face_ID = detected_faces[0].face_id

multi_face_image_url = "https://auth.etna-alternance.net/api/users/lequer_r/photo"
multi_image_name = os.path.basename(multi_face_image_url)

detected_faces2 = face_client.face.detect_with_url(url=multi_face_image_url, detection_model='detection_03')


print('Detected face IDs from', multi_image_name, ':')
if not detected_faces2:
	raise Exception('No face detected from image {}.'.format(multi_image_name))
else:
    for face in detected_faces2:
        print(face.face_id)
print()


single_face_image_url = 'https://raw.githubusercontent.com/Microsoft/Cognitive-Face-Windows/master/Data/detection1.jpg'
single_image_name = os.path.basename(single_face_image_url)

detected_faces = face_client.face.detect_with_url(url=single_face_image_url, detection_model='detection_03')
if not detected_faces:
	raise Exception('No face detected from image {}'.format(single_image_name))


def getRectangle(faceDictionary):
    rect = faceDictionary.face_rectangle
    left = rect.left
    top = rect.top
    right = left + rect.width
    bottom = top + rect.height
    
    return ((left, top), (right, bottom))

def drawFaceRectangles() :

    response = requests.get(single_face_image_url)
    img = Image.open(BytesIO(response.content))

    print('Drawing rectangle around face... see popup for results.')
    draw = ImageDraw.Draw(img)
    for face in detected_faces:
        draw.rectangle(getRectangle(face), outline='red')

    im = Image.open('https://auth.etna-alternance.net/api/users/lequer_r/photo')
    img.show()


print()


print('-----------------------------')
print()
print('FIND SIMILAR')
print()

second_image_face_IDs = list(map(lambda x: x.face_id, detected_faces2))

similar_faces = face_client.face.find_similar(face_id=first_image_face_ID, face_ids=second_image_face_IDs)
if not similar_faces:
	print('No similar faces found in', multi_image_name, '.')

else:
	print('Similar faces found in', multi_image_name + ':')
	for face in similar_faces:
		first_image_face_ID = face.face_id
		
		face_info = next(x for x in detected_faces2 if x.face_id == first_image_face_ID)
		if face_info:
			print('  Face ID: ', first_image_face_ID)
			print('  Face rectangle:')
			print('    Left: ', str(face_info.face_rectangle.left))
			print('    Top: ', str(face_info.face_rectangle.top))
			print('    Width: ', str(face_info.face_rectangle.width))
			print('    Height: ', str(face_info.face_rectangle.height))

print()

print('-----------------------------')
print()
print('VERIFY')
print()

target_image_file_names = ['Family1-Dad1.jpg', 'Family1-Dad2.jpg']

source_image_file_name1 = 'Family1-Dad3.jpg'
source_image_file_name2 = 'Family1-Son1.jpg'

detected_faces1 = face_client.face.detect_with_url(IMAGE_BASE_URL + source_image_file_name1, detection_model='detection_03')

source_image1_id = detected_faces1[0].face_id
print('{} face(s) detected from image {}.'.format(len(detected_faces1), source_image_file_name1))

detected_faces2 = face_client.face.detect_with_url(IMAGE_BASE_URL + source_image_file_name2, detection_model='detection_03')

source_image2_id = detected_faces2[0].face_id
print('{} face(s) detected from image {}.'.format(len(detected_faces2), source_image_file_name2))


detected_faces_ids = []

for image_file_name in target_image_file_names:
	
    detected_faces = face_client.face.detect_with_url(IMAGE_BASE_URL + image_file_name, detection_model='detection_03')
    
    detected_faces_ids.append(detected_faces[0].face_id)
    print('{} face(s) detected from image {}.'.format(len(detected_faces), image_file_name))

verify_result_same = face_client.face.verify_face_to_face(source_image1_id, detected_faces_ids[0])
print('Faces from {} & {} are of the same person, with confidence: {}'
    .format(source_image_file_name1, target_image_file_names[0], verify_result_same.confidence)
    if verify_result_same.is_identical
    else 'Faces from {} & {} are of a different person, with confidence: {}'
        .format(source_image_file_name1, target_image_file_names[0], verify_result_same.confidence))


verify_result_diff = face_client.face.verify_face_to_face(source_image2_id, detected_faces_ids[0])
print('Faces from {} & {} are of the same person, with confidence: {}'
    .format(source_image_file_name2, target_image_file_names[0], verify_result_diff.confidence)
    if verify_result_diff.is_identical
    else 'Faces from {} & {} are of a different person, with confidence: {}'
        .format(source_image_file_name2, target_image_file_names[0], verify_result_diff.confidence))

print()

print('-----------------------------')
print()
print('PERSON GROUP OPERATIONS')
print()



print('Person group:', PERSON_GROUP_ID)
face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)


woman = face_client.person_group_person.create(PERSON_GROUP_ID, "Woman")

man = face_client.person_group_person.create(PERSON_GROUP_ID, "Man")

child = face_client.person_group_person.create(PERSON_GROUP_ID, "Child")


woman_images = [file for file in glob.glob('*.jpg') if file.startswith("w")]
man_images = [file for file in glob.glob('*.jpg') if file.startswith("m")]
child_images = [file for file in glob.glob('*.jpg') if file.startswith("ch")]


for image in woman_images:
    w = open(image, 'r+b')
    face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, woman.person_id, w)


for image in man_images:
    m = open(image, 'r+b')
    face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, man.person_id, m)

for image in child_images:
    ch = open(image, 'r+b')
    face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, child.person_id, ch)


print()
print('Training the person group...')

face_client.person_group.train(PERSON_GROUP_ID)

while (True):
    training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
        sys.exit('Training the person group has failed.')
    time.sleep(5)


test_image_array = glob.glob('test-image-person-group.jpg')
image = open(test_image_array[0], 'r+b')

print('Pausing for 60 seconds to avoid triggering rate limit on free account...')
time.sleep (60)


face_ids = []

faces = face_client.face.detect_with_stream(image, detection_model='detection_03')
for face in faces:
    face_ids.append(face.face_id)

results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
print('Identifying faces in {}'.format(os.path.basename(image.name)))
if not results:
    print('No person identified in the person group for faces from {}.'.format(os.path.basename(image.name)))
for person in results:
	if len(person.candidates) > 0:
		print('Person for face ID {} is identified in {} with a confidence of {}.'.format(person.face_id, os.path.basename(image.name), person.candidates[0].confidence)) # Get topmost confidence score
	else:
		print('No person identified for face ID {} in {}.'.format(person.face_id, os.path.basename(image.name)))

print()

print('-----------------------------')
print()
print('LARGE PERSON GROUP OPERATIONS')
print()


LARGE_PERSON_GROUP_ID = str(uuid.uuid4()) 
print('Large person group:', LARGE_PERSON_GROUP_ID)
face_client.large_person_group.create(large_person_group_id=LARGE_PERSON_GROUP_ID, name=LARGE_PERSON_GROUP_ID)


woman = face_client.large_person_group_person.create(LARGE_PERSON_GROUP_ID, "Woman")

man = face_client.large_person_group_person.create(LARGE_PERSON_GROUP_ID, "Man")

child = face_client.large_person_group_person.create(LARGE_PERSON_GROUP_ID, "Child")



woman_images = [file for file in glob.glob('*.jpg') if file.startswith("w")]
man_images = [file for file in glob.glob('*.jpg') if file.startswith("m")]
child_images = [file for file in glob.glob('*.jpg') if file.startswith("ch")]


for image in woman_images:
    w = open(image, 'r+b')
    face_client.large_person_group_person.add_face_from_stream(LARGE_PERSON_GROUP_ID, woman.person_id, w)


for image in man_images:
    m = open(image, 'r+b')
    face_client.large_person_group_person.add_face_from_stream(LARGE_PERSON_GROUP_ID, man.person_id, m)


for image in child_images:
    ch = open(image, 'r+b')
    face_client.large_person_group_person.add_face_from_stream(LARGE_PERSON_GROUP_ID, child.person_id, ch)

print()
print('Training the large person group...')

face_client.large_person_group.train(LARGE_PERSON_GROUP_ID)

while (True):
    training_status = face_client.large_person_group.get_training_status(LARGE_PERSON_GROUP_ID)
    print("Training status: {}.".format(training_status.status))
    print()
    if (training_status.status is TrainingStatusType.succeeded):
        break
    elif (training_status.status is TrainingStatusType.failed):
        sys.exit('Training the large person group has failed.')
    time.sleep(5)

person_list_large = face_client.large_person_group_person.list(large_person_group_id=LARGE_PERSON_GROUP_ID, start='')

print('Persisted Face IDs from {} large person group persons:'.format(len(person_list_large)))
print()
for person_large in person_list_large:
    for persisted_face_id in person_large.persisted_face_ids:
        print('The person {} has an image with ID: {}'.format(person_large.name, persisted_face_id))
print()


face_client.large_person_group.delete(LARGE_PERSON_GROUP_ID)
print("Deleted the large person group.")
print()

print('-----------------------------')
print()
print('FACELIST OPERATIONS')
print()


image_file_names = [
    "Family1-Dad1.jpg",
    "Family1-Daughter1.jpg",
    "Family1-Mom1.jpg",
    "Family1-Son1.jpg",
    "Family2-Lady1.jpg",
    "Family2-Man1.jpg",
    "Family3-Lady1.jpg",
    "Family3-Man1.jpg"
]


face_list_id = "my-face-list"
print("Creating face list: {}...".format(face_list_id))
print()
face_client.face_list.create(face_list_id=face_list_id, name=face_list_id)


for image_file_name in image_file_names:
    face_client.face_list.add_face_from_url(
        face_list_id=face_list_id,
        url=IMAGE_BASE_URL + image_file_name,
        user_data=image_file_name
    )


the_face_list = face_client.face_list.get(face_list_id)
if not the_face_list :
    raise Exception("No persisted face in face list {}.".format(face_list_id))

print('Persisted face ids of images in face list:')
print()
for persisted_face in the_face_list.persisted_faces:
    print(persisted_face.persisted_face_id)


face_client.face_list.delete(face_list_id=face_list_id)
print()
print("Deleted the face list: {}.\n".format(face_list_id))

print('-----------------------------')
print()
print('LARGE FACELIST OPERATIONS')
print()


image_file_names_large = [
    "Family1-Dad1.jpg",
    "Family1-Daughter1.jpg",
    "Family1-Mom1.jpg",
    "Family1-Son1.jpg",
    "Family2-Lady1.jpg",
    "Family2-Man1.jpg",
    "Family3-Lady1.jpg",
    "Family3-Man1.jpg"
]


large_face_list_id = "my-large-face-list"
print("Creating large face list: {}...".format(large_face_list_id))
print()
face_client.large_face_list.create(large_face_list_id=large_face_list_id, name=large_face_list_id)


for image_file_name in image_file_names_large:
    face_client.large_face_list.add_face_from_url(
        large_face_list_id=large_face_list_id,
        url=IMAGE_BASE_URL + image_file_name,
        user_data=image_file_name
    )


print("Train large face list {}".format(large_face_list_id))
print()
face_client.large_face_list.train(large_face_list_id=large_face_list_id)


while (True):
    training_status_list = face_client.large_face_list.get_training_status(large_face_list_id=large_face_list_id)
    print("Training status: {}.".format(training_status_list.status))
    if training_status_list.status is TrainingStatusType.failed:
        raise Exception("Training failed with message {}.".format(training_status_list.message))
    if (training_status_list.status is TrainingStatusType.succeeded):
        break
    time.sleep(5)


large_face_list_faces = face_client.large_face_list.list_faces(large_face_list_id)
if not large_face_list_faces :
    raise Exception("No persisted face in face list {}.".format(large_face_list_id))

print('Face ids of images in large face list:')
print()
for large_face in large_face_list_faces:
    print(large_face.persisted_face_id)


face_client.large_face_list.delete(large_face_list_id=large_face_list_id)
print()
print("Deleted the large face list: {}.\n".format(large_face_list_id))

print('-----------------------------')
print()
print('DELETE PERSON GROUP')
print()

face_client.person_group.delete(person_group_id=PERSON_GROUP_ID)
print("Deleted the person group {} from the source location.".format(PERSON_GROUP_ID))
print()


print()
print('-----------------------------')
print()
print('End of quickstart.')
