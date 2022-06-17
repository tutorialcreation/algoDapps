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

class AssetViewSet(viewsets.ModelViewSet):

    serializer_class = AssetSerializer
    queryset = Asset.objects.all()


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user)

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
        client = getAlgodClient()
        creator = None
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
        application = Application()
        application.app_id = appID
        application.app_nft = nft
        application.save()

        return Response(data={
            'appID':application.app_id
        },status=status.HTTP_201_CREATED)




