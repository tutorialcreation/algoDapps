from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
from algosdk import account,encoding
from algosdk.logic import get_application_address
from pyteal import compileTeal, Mode
from .account import Account



def createAuctionApplication(
    client:AlgodClient,
    sender:Account,
    seller:str,
    nftID:str,
    startTime:int,
    endTime:int,
    reserve:int,
    minBidIncrement:int
):
    pass
