import time
import cv2
import pickle
import face_recognition
import requests
import os


name = ''


def sign_up():
    print("Signing Up")

    try:
        with open('face_data.dat', 'rb') as f:
            known_face_data = pickle.load(f)
        known_face_encodings = known_face_data['encodings']
        known_face_labels = known_face_data['labels']
    except FileNotFoundError:
        known_face_encodings = []
        known_face_labels = []

    # Warm-up loop to allow the camera to adjust
    for i in range(10):
        ret, frame = cv2.imread()
        if not ret:
            print("Failed to capture image")
            exit()
        time.sleep(0.1)  # Sleep for 100 milliseconds

    # Capture a single frame
    ret, frame = cv2.read()

    if frame is not None:
        # Find all the faces and their encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(
            frame, face_locations)

        # Prompt user to enter a label for the face
        if len(face_encodings) > 0:
            # cv2.imshow('Video', frame)
            global name
            name = input("Enter Name: ")
            known_face_encodings.append(face_encodings[0])
            known_face_labels.append(name)

        # Save known face encodings and corresponding labels to file
        with open('face_data.dat', 'wb') as f:
            pickle.dump({'encodings': known_face_encodings,
                        'labels': known_face_labels}, f)
            print("Saved the Face on file!")
            f.close()
            cv2.release()
    else:
        print("Signup Incomplete")

    # Check if the frame was captured correctly
    if not ret:
        print("Failed to capture image")
        exit()

def log_in(image):
    try:
        with open('face_data.dat', 'rb') as f:
            known_face_data = pickle.load(f)
        known_face_encodings = known_face_data['encodings']
        known_face_labels = known_face_data['labels']
    except FileNotFoundError:
        known_face_encodings = []
        known_face_labels = []

    # Warm-up loop to allow the camera to adjust
    for i in range(10):
        ret, frame = cv2.imread(image)
        if not ret:
            print("Failed to capture image")
            exit()
        time.sleep(0.1)  # Sleep for 100 milliseconds

    # Capture frame
    ret, frame = cv2.imread()
    if frame is not None:
        # Find all the faces and their encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(
            frame, face_locations)

        # Initialize matches as an empty list
        matches = []

        # Loop through each face found in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare the current face encoding with the known face encodings
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding)

        # If a match is found, display a welcome message and stop capturing video
        if True in matches:
            name = known_face_labels[matches.index(True)]
            print("Authentication successful! Welcome, " + name + "!")
            # cv2.putText(frame, "Authentication successful! Welcome, " + label + "!",
            #             (left-10, bottom+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.release()
            cv2.destroyAllWindows()
            return 1
        else:
            print("Face Not Found!\nTry Again!")
            time.sleep(0.5)

    else:
        print("Waiting for webcam...")

def clear_face_data():
    os.remove('face_data.dat')


# Verbwire
def mint_custom_nft(data, username):

    data = 'face_data.dat'

    url = "https://api.verbwire.com/v1/nft/mint/mintFromMetadata"

    payload = f"""\
    -----011000010111000001101001\r
    Content-Disposition: form-data; name="quantity"\r
    \r
    1\r
    -----011000010111000001101001\r
    Content-Disposition: form-data; name="chain"\r
    \r
    goerli\r
    -----011000010111000001101001\r
    Content-Disposition: form-data; name="contractAddress"\r
    \r
    0xc83E1Dad8fC1A872420154dFbb5b318aaf769940\r
    -----011000010111000001101001\r
    Content-Disposition: form-data; name="data"\r
    \r
    {data}\r
    -----011000010111000001101001\r
    Content-Disposition: form-data; name="recipientAddress"\r
    \r
    0x717aeB89048f10061C0dCcdEB2592a60bA4F1a79\r
    -----011000010111000001101001\r
    Content-Disposition: form-data; name="name"\r
    \r
    {username}\r
    -----011000010111000001101001--\r
    """
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        "X-API-Key": "sk_live_2fdf410e-680e-482a-9488-3d042640ff3e"
    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)

    url = "https://api.verbwire.com/v1/nft/mint/quickMintFromFile"

    payload = f"""-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"allowPlatformToOperateToken\"\r\n\r\ntrue\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"chain\"\r\n\r\nethereum\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{data}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\nFace Data for Face Auth\r\n-----011000010111000001101001--\r\n\r\n"""
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        "X-API-Key": "sk_live_2fdf410e-680e-482a-9488-3d042640ff3e"
    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)

    return response.text

# Verbwire
def get_nft_attributes():
    url = "https://api.verbwire.com/v1/nft/data/owned?walletAddress=0x717aeB89048f10061C0dCcdEB2592a60bA4F1a79&chain=goerli"
    headers = {
        "accept": "application/json",
        "X-API-Key": "sk_live_b7159a98-601c-455e-b0e8-fd8cb42b48b3"
    }
    response = requests.get(url, headers=headers)

    data = response.json()
    token_attributes = []

    for nft in data['nfts']:
        contract_address = nft['contractAddress']
        if contract_address == "0xc83E1Dad8fC1A872420154dFbb5b318aaf769940".lower():
            token_id = nft["tokenID"]
            chain = "goerli"
            url_inner = f"https://api.verbwire.com/v1/nft/data/nftDetails?contractAddress={contract_address}&tokenId={token_id}&chain={chain}"
            headers = {
                "accept": "application/json",
                "X-API-Key": "sk_live_b7159a98-601c-455e-b0e8-fd8cb42b48b3"
            }
            url_resp = requests.get(url_inner, headers=headers)
            json_data = url_resp.json()
            token_uri = json_data['nft_details']['tokenURI']
            main_resp = requests.get(token_uri).json()
            token_attributes.appends(main_resp['attributes'])
    return token_attributes

# Verbwire - still in production
def mint_nft(data):
    import requests

    url = "https://api.verbwire.com/v1/nft/store/file"


    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data",
        "X-API-Key": "sk_live_6f08dc8c-d422-4989-9270-d45e516b714a"
    }

    response = requests.post(url, headers=headers)

    print(response.text)
    
    import requests

    url = "https://api.verbwire.com/v1/nft/mint/quickMintFromMetadata"

    payload = f"""-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"chain\"\r\n\r\nethereum\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"imageUrl\"\r\n\r\n{data}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\nFace_Auth\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\nFace Auth Binary\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"recipientAddress\"\r\n\r\nv2mLFKD_bn6LP_B18Ca8-\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"data\"\r\n\r\n{data}\r\n-----011000010111000001101001--\r\n\r\n"""
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        "X-API-Key": "sk_live_2fdf410e-680e-482a-9488-3d042640ff3e"
    }

    response = requests.post(url, data=payload, headers=headers)

    print(response.text)


def menu():
    choice = 0

    while int(choice) != 5:
        print("1. Sign Up")
        print("2. Sign In")
        print("3. Clear Face Data")
        print("4. Mint NFT")
        print("5. Exit")
        choice = input("Enter Choice: ")
        print(choice)

        if (int(choice) == 1):
            sign_up()
        elif (int(choice) == 2):
            log_in()
        elif (int(choice) == 3):
            clear_face_data()
        elif (int(choice) == 4):
            mint_nft('face_data.dat')
