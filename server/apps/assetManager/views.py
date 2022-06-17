from django.shortcuts import get_object_or_404
from rest_framework import viewsets,status
from rest_framework.response import Response 
from apps.assetManager.models import Application, Asset,Nft 
from apps.assetManager.serializers import AssetSerializer
from django.contrib.auth.models import User
import os,sys
import json

sys.path.append(os.path.abspath(os.path.join('../')))
from time import time, sleep

from algosdk import account, encoding
from algosdk.logic import get_application_address
from algosdk.future import transaction
from auction.operations import createAuctionApp, setupAuctionApp, placeBid, closeAuction
from auction.util import (
    getBalances,
    getAppGlobalState,
    getLastBlockTimestamp,
)
from auction.testing.setup import getAlgodClient
from auction.testing.resources import (
    getTemporaryAccount,
    optInToAsset,
    createDummyAsset,
)
from auction.util import waitForTransaction
from auction.account import Account

class AssetViewSet(viewsets.ModelViewSet):

    serializer_class = AssetSerializer
    queryset = Nft.objects.all()


    def get_algod_client_details(self,request,*args,**kwargs):
        user_id = request.data.get('user_id')
    
        client = getAlgodClient()
        account = getTemporaryAccount(client)
        user = get_object_or_404(User,id=user_id)
        nft = Nft()
        nft.address = account.getAddress()
        nft.sk = account.getPrivateKey()
        nft.user = user
        for group in user.groups.all():
            nft.role = group
       
        nft.save()
        
        return Response(data={
            'pk':nft.pk,
            'address':nft.address,
            'sk':nft.sk,
            'role':nft.role.id,
            'user':nft.user.id
        },status=status.HTTP_200_OK)

    def gen_nft(self,request,*args,**kwargs):
        nft_pk = request.data.get('nft_pk')
        total = request.data.get('nft_amount')
        unit_name = request.data.get('unit_name')
        asset_name = request.data.get('asset_name')
        url = request.data.get('url')
        note = request.data.get('note')

        nft = get_object_or_404(Nft,pk=nft_pk)
        nft.amount = total
        nft.save()


        client = getAlgodClient()
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
        signedTxn = txn.sign(nft.sk)

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
            'address':nft.address,
            'sk':nft.sk
        },status=status.HTTP_201_CREATED)


    def gen_app(self,request,*args,**kwargs):
        nftId = request.data.get('nft_id')

        nft = get_object_or_404(Nft,nft_id=nftId)
        startTime = int(time()) + int(request.data.get('start_time'))
        endTime = startTime + int(request.data.get('end_time'))
        reserve = int(request.data.get('reserve'))
        increment = int(request.data.get('increment'))
        creator_address = request.data.get('creator')
        nft_amount = request.data.get('nft_amount')
        creator_nft = get_object_or_404(Nft,address=creator_address)

        client = getAlgodClient()
        creator = Account(creator_nft.sk)
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
        nftHolder = Account(nft.sk)
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
        application.save()

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
        
        funder = Account(funder_nft.sk)
        nftHolder = Account(nftHolder_nft.sk)

        client = getAlgodClient()
        setupAuctionApp(
            client=client,
            appID=appId,
            funder=funder,
            nftHolder=nftHolder,
            nftID=nftId,
            nftAmount=nftAmount,
        )

        return Response(data={
            f'successfully transferred {nftAmount} Algos  from {funder_address} to {nftHolder_address}'
        },status=status.HTTP_200_OK)


    def request_asset(self,request,*args,**kwargs):
        appId = request.data.get('appId')
        bidder_address = request.data.get('bidder')
        bid_amount = request.data.get('bidAmount')
        bidder_nft = get_object_or_404(Nft,address=bidder_address)
        bidder_nft.is_bidder = True
        bidder_nft.save()
        bidder = Account(bidder_nft.sk)
        client = getAlgodClient()
        placeBid(client=client, 
                appID=appId, 
                bidder=bidder, 
                bidAmount=bid_amount
        )
        
        return Response(data={
            'bidder_address':bidder_nft.address
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

    
        


