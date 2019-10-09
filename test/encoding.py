import base64

password="0002692b-4ddc-4003-ba61-544d5b84ce9f"
passwordB64 = base64.b64encode(bytes(password, "UTF-8")).decode("ascii").rstrip('\n')
print(passwordB64)
