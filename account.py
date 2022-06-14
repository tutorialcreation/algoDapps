from algosdk import account,mnemonic
from algosdk.error import EmptyAddressError
import logging

class Account:
    """
    - getting private key and address for an account
    """

    def __init__(self, privateKey:str=None) -> None:
        try:
            self.sk = privateKey
            self.addr = account.address_from_private_key(privateKey)
        except:
            try:
                self.sk,self.addr = account.generate_account()
            except EmptyAddressError as ea:
                logging.error(ea)

    def getAddress(self)->str:
        return self.addr
    
    def getPrivateKey(self)->str:
        return self.sk

    def getMnemonic(self)->str:
        return mnemonic.from_private_key(self.sk)

    @classmethod
    def FromMnemonic(cls,m:str)->"Account":
        return cls(mnemonic.to_private_key(m))


if __name__=='__main__':
    print("test area")