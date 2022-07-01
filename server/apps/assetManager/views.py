from django.shortcuts import get_object_or_404
from rest_framework import viewsets,status
from rest_framework.response import Response 
from apps.assetManager.models import Application, Asset,Nft 
from apps.assetManager.serializers import AssetSerializer

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import os,sys
import json

User=get_user_model()
purestake_key = 'REPLACE WITH YOUR PURESTAKE API KEY'
endpoint_address = 'https://testnet-algorand.api.purestake.io/ps1'
purestake_header = {'X-Api-key': purestake_key}

sys.path.append(os.path.abspath(os.path.join('../')))
from time import time, sleep

from algosdk import account, encoding,mnemonic
from algosdk import algod
from algosdk.wallet import Wallet
from algosdk.logic import get_application_address
from algosdk.future import transaction
from auction.operations import createAuctionApp, donate, setupAuctionApp, placeBid, closeAuction
from auction.util import (
    getBalances,
    getAppGlobalState,
    getLastBlockTimestamp,
    waitForTransaction,
    get_created_asset,
    get_asset_holding

)
from auction.testing.setup import (
    KMD_WALLET_NAME,
    KMD_WALLET_PASSWORD,
    getAlgodClient,
    getKmdClient,
    getGenesisAccounts,
)
from auction.testing.resources import (
    getTemporaryAccount,
    optInToAsset,
    createDummyAsset,
)
from auction.account import Account
from .helpers import decoded_token

class AssetViewSet(viewsets.ModelViewSet):

    serializer_class = AssetSerializer
    queryset = Asset.objects.all()


    def connect_wallet(self,request,*args,**kwargs):
        address = request.data.get('address')

        # pick the last account always
        nft,_ = Nft.objects.update_or_create(
            address = address
        
        )

        return Response(data={
            'address':nft.address,
        },status=status.HTTP_200_OK)



    def gen_nft(self,request,*args,**kwargs):
        
        address = request.data.get('address')
        user_id = decoded_token(request)
        user = get_object_or_404(User,id=user_id)
        group = get_object_or_404(Group,id=user.role)
        total = request.data.get('nft_amount')
        unit_name = request.data.get('unit_name')
        asset_name = request.data.get('asset_name')
        url = request.data.get('url')
        note = request.data.get('note')

        nft = Nft.objects.filter(address=address).last()
        nft.amount = total
        nft.user = user
        nft.role = group
        nft.save()

        wallet = Wallet(KMD_WALLET_NAME, KMD_WALLET_PASSWORD, getKmdClient())
        mnemonics = request.data.get('mnemonic')
        pk = mnemonic.to_private_key(mnemonics)
        try:
            wallet.import_key(pk)
        except Exception as e:
            print(e)



        my_account = None
        accounts = getGenesisAccounts()
        for account in accounts:
            if address == account.getAddress():
                my_account = account
        
        client  = getAlgodClient()

        
        txn = transaction.AssetCreateTxn(
            sender=nft.address,
            total=nft.amount,
            decimals=0,
            default_frozen=False,
            manager=nft.address,
            reserve=nft.address,
            freeze=nft.address,
            clawback=nft.address,
            unit_name=unit_name,
            asset_name=asset_name,
            url=url,
            note=note,
            sp=client.suggested_params(),
        )

        signedTxn = txn.sign(my_account.getPrivateKey())

        client.send_transaction(signedTxn)

        response = waitForTransaction(client, signedTxn.get_txid())
        assert response.assetIndex is not None and response.assetIndex > 0
        nft.nft_id = response.assetIndex
        nft.save()

        asset = Asset()
        asset.nft = nft
        asset.unit_name = unit_name
        asset.asset_name = asset_name
        asset.asset_url = url
        asset.note = note
        asset.save()


        return Response(data={
            'nft_id':nft.nft_id,
            'amount':nft.amount,
            'address':nft.address
        },status=status.HTTP_201_CREATED)


    def gen_app(self,request,*args,**kwargs):
        nftId = request.data.get('nft_id')

        nft = get_object_or_404(Nft,nft_id=nftId)
        startTime = int(time()) + int(request.data.get('start_time'))
        endTime = startTime + int(request.data.get('end_time'))
        reserve = int(request.data.get('reserve'))
        increment = int(request.data.get('increment'))
        creator_address = request.data.get('creator')
        address_ = Nft.objects.filter(address=creator_address)
        nft_amount = request.data.get('nft_amount')
        creator = None
        if address_.exists():
            

            creator_nft = get_object_or_404(Nft,address=creator_address)

            
        
        else:
            creator_nft,_=Nft.objects.update_or_create(
                address=creator_address
            )

        client = getAlgodClient()
        accounts = getGenesisAccounts()
        for account in accounts:
            if creator_nft.address == account.getAddress():
                creator = account

        appID = createAuctionApp(
            client=client,
            sender=creator,
            seller=nft.address,
            nftID=nft.nft_id,
            startTime=startTime,
            endTime=endTime,
            reserve=reserve,
            minBidIncrement=increment,
        )
        nftHolder = None
        for account in accounts:
            if nft.address == account.getAddress():
                nftHolder = account

        setupAuctionApp(
            client=client,
            appID=appID,
            funder=creator,
            nftHolder=nftHolder,
            nftID=nftId,
            nftAmount=nft_amount,
        )
        application = Application()
        application.app_id = appID
        application.app_nft = nft
        application.start_time = startTime
        application.end_time = endTime
        application.save()
        sleep(5)

        return Response(data={
            'appID':application.app_id,
            'funder':creator_nft.address,
            'nftHolder':nft.address,
            'nftId':nft.nft_id,
            'nftAmount':nft.amount
        },status=status.HTTP_201_CREATED)

    
    def donate_assets(self,request,*args,**kwargs):
        nftId = request.data.get('nft_id')
        appId = request.data.get('app_id')
        funder_address = request.data.get('funder')
        nftHolder_address = request.data.get('nft_holder')
        nftAmount = request.data.get('nft_amount')

        funder_nft = get_object_or_404(Nft,address=funder_address)
        nftHolder_nft = get_object_or_404(Nft,address=nftHolder_address)
        nftHolder = None
        accounts = getGenesisAccounts()
        
        for account in accounts:
            if nftHolder_nft.address == account.getAddress():
                nftHolder = account

        funder = None
        for account in accounts:
            if funder_nft.address == account.getAddress():
                funder = account
        

        client = getAlgodClient()
        
        unsigned_txn = transaction.PaymentTxn(
            funder.getAddress(), 
            client.suggested_params(), 
            nftHolder.getAddress(),
            nftAmount
        )

        signed_txn = unsigned_txn.sign(funder.getPrivateKey())
        client.send_transaction(signed_txn)

        response = waitForTransaction(client, signed_txn.get_txid())
        print(response)
        return Response(data={
            f'successfully transferred {nftAmount} Algos  from {funder_address} to {nftHolder_address}'
        },status=status.HTTP_200_OK)


    def request_asset(self,request,*args,**kwargs):
        appId = request.data.get('appId')
        bidder_address = request.data.get('bidder')
        bid_amount = request.data.get('bidAmount')
        nft_id = request.data.get('nft_id')
        address_ = Nft.objects.filter(address=bidder_address)
        bidder = None
        app = get_object_or_404(Application,app_id=appId)
        if address_.exists():
    

            bidder_nft = get_object_or_404(Nft,address=bidder_address)

    
        
        else:
            bidder_nft,_=Nft.objects.update_or_create(
                address=bidder_address
            )

        client = getAlgodClient()
        accounts = getGenesisAccounts()
        for account in accounts:
            if bidder_nft.address == account.getAddress():
                bidder = account

        


        bidder_nft.is_bidder = True
        bidder_nft.save()
        client = getAlgodClient()
        _, lastRoundTime = getLastBlockTimestamp(client)
        print(lastRoundTime,app.start_time)
        if lastRoundTime < app.start_time + 5:
            sleep(app.start_time + 5 - lastRoundTime)
        else:
            sleep(lastRoundTime + 5 - lastRoundTime)
        placeBid(client=client, 
                appID=appId, 
                bidder=bidder, 
                bidAmount=bid_amount
        )
        nft = get_object_or_404(Nft,nft_id=nft_id)
        optInToAsset(client, nft_id, bidder)
        asset = Asset.objects.filter(nft=nft)
        bidded_asset = None
        if asset.exists():
            bidded_asset = asset.last()
            bidded_asset.is_bidded = True
            bidded_asset.bidders.add(bidder_nft)
            bidded_asset.save()
        
        
        return Response(data={
            'bidder_address':bidder_nft.address,
            # 'asset_url':bidded_asset.asset_url
        })


    def optIn(self,request,*args,**kwargs):
        nft_id = request.data.get('nft_id')
        bidder_address = request.data.get('bidder')
        bidder_nft = get_object_or_404(Nft,address=bidder_address)
        nft = get_object_or_404(Nft,nft_id=nft_id)
        client = getAlgodClient()
        bidder = Account(bidder_nft.sk)
        optInToAsset(client, nft_id, bidder)
        asset = Asset.objects.filter(nft=nft)
        bidded_asset = None
        if asset.exists():
            bidded_asset = asset.last()
            bidded_asset.is_bidded = True
            bidded_asset.bidders.add(bidder_nft)
            bidded_asset.save()
        
        return Response(data={
            'bidder':bidder_address,
            'asset':bidded_asset.asset_url
        },status=status.HTTP_201_CREATED)

    
    def accept_request(self,request,*args,**kwargs):
        nft_id = request.data.get('nft_id')
        app_id = request.data.get('app_id')
        nft = get_object_or_404(Nft,nft_id=nft_id)
        nftHolder = None
        accounts = getGenesisAccounts()
        for account in accounts:
            if nft.address == account.getAddress():
                nftHolder = account
        client = getAlgodClient()
        closeAuction(client,app_id,nftHolder)  
        asset = Asset.objects.filter(nft=nft).last()

        return Response(data={
            'asset':asset.asset_url
        },status=status.HTTP_200_OK)      


    def get_created_asset(self,request,*args,**kwargs):
        nft_id = request.data.get('nft_id')
        nft = get_object_or_404(Nft,nft_id=nft_id)
        address = request.data.get('address')
        nft_account = get_object_or_404(Nft,address=address)
        

        client = getAlgodClient()
        asset = get_created_asset(client,nft_account.address,nft.nft_id)
        
        return Response(json.loads(asset),status=status.HTTP_200_OK)

    def get_asset_holding(self,request,*args,**kwargs):

        nft_id = request.data.get('nft_id')
        nft = get_object_or_404(Nft,nft_id=nft_id)
        address = request.data.get('address')
        nft_account = get_object_or_404(Nft,address=address)
        

        client = getAlgodClient()
        asset = get_asset_holding(client,nft_account.address,nft.nft_id)
        
        return Response(json.loads(asset),status=status.HTTP_200_OK)


    def get_balances(self,request,*args,**kwargs):
        address = request.data.get('address')
        nft = get_object_or_404(Nft,address=address)

        client = getAlgodClient()
        balance = getBalances(client,nft.address)
        return Response(data=balance,status=status.HTTP_200_OK)

