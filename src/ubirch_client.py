import requests
from uuid import UUID
import ubirch


class UbirchClient(ubirch.Protocol):
    def __init__(self, key_store: ubirch.KeyStore, register_url: str, uuid: UUID) -> None:
        super().__init__()
        self.__ks = key_store
        self.__register_url = register_url
        self.__uuid = uuid

        self._create_identity()

    def _sign(self, uuid: UUID, message: bytes) -> bytes:
        return self.__ks.find_signing_key(uuid).sign(message)

    def _verify(self, uuid: UUID, message: bytes, signature: bytes) -> None:
        return self.__ks.find_verifying_key(uuid).verify(signature, message)

    def _create_identity(self):
        if not self.__ks.exists_signing_key(self.__uuid):
            self.__ks.create_ed25519_keypair(self.__uuid)

        keyreg_upp = self.message_signed(self.__uuid, 0x01, self.__ks.get_certificate(self.__uuid))
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
