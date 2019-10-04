import binascii
import json
from uuid import UUID

import ed25519
import msgpack
import requests
import ubirch
from ubirch_protocol import Protocol


class UbirchClient(Protocol):
    PUB_DEV = ed25519.VerifyingKey(
        b'\xa2\x40\x3b\x92\xbc\x9a\xdd\x36\x5b\x3c\xd1\x2f\xf1\x20\xd0\x20\x64\x7f\x84\xea\x69\x83\xf9\x8b\xc4\xc8\x7e\x0f\x4b\xe8\xcd\x66')

    def __init__(self, uuid: UUID, key_store: ubirch.KeyStore, register_url: str, update_url: str,
                 headers: dict) -> None:
        super().__init__()
        self.__uuid = uuid
        self.__ks = key_store
        self.__headers = headers
        self.__register_url = register_url
        self.__update_url = update_url

        self._create_identity()

    def _sign(self, uuid: UUID, message: bytes) -> bytes:
        return self.__ks.find_signing_key(uuid).sign(message)

    def _verify(self, uuid: UUID, message: bytes, signature: bytes) -> None:
        if str(uuid) == str(self.__uuid):
            return self.__ks.find_verifying_key(uuid).verify(signature, message)
        else:
            return self.PUB_DEV.verify(signature, message)

    def _create_identity(self):
        if not self.__ks.exists_signing_key(self.__uuid):
            self.__ks.create_ed25519_keypair(self.__uuid)

        keyreg_upp = self.message_signed(self.__uuid, 0x01, self.__ks.get_certificate(self.__uuid), legacy=True)
        r = requests.post(self.__register_url,
                          headers={'Content-Type': 'application/octet-stream'},
                          data=keyreg_upp)

        if r.status_code == 200:
            r.close()
            print(str(self.__uuid) + ": identity registered")
        else:
            print(str(self.__uuid) + ": ERROR: device identity not registered")
            raise Exception(
                "!! request to {} failed with status code {}: {}".format(self.__register_url, r.status_code,
                                                                         r.text))

    def send(self, payload: dict):
        serialized = json.dumps(payload)
        upp = self.message_chained(self.__uuid, 0x00, self._hash(msgpack.packb(serialized)))
        r = requests.post(self.__update_url, headers=self.__headers, data=upp)
        if r.status_code == 200:
            try:
                self.message_verify(r.content)
                print("response verified")
            except Exception as e:
                raise Exception("!! response verification failed: {}. {}".format(e, binascii.hexlify(r.content)))
        else:
            raise Exception(
                "!! request to {} failed with status code {}: {}".format(self.__update_url, r.status_code, r.text))
