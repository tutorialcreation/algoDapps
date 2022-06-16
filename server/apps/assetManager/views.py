from rest_framework import viewsets,status
from rest_framework.response import Response 
from apps.assetManager.models import Asset 
from apps.assetManager.serializers import AssetSerializer
import os,sys
import json
sys.path.append(os.path.abspath(os.path.join('../')))
from time import time, sleep

from algosdk import account, encoding
from algosdk.logic import get_application_address
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

class AssetViewSet(viewsets.ModelViewSet):

    serializer_class = AssetSerializer
    queryset = Asset.objects.all()


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user)

    def get_algod_client_details(self,request,*args,**kwargs):
        client = getAlgodClient()
        creator = getTemporaryAccount(client)
        seller = getTemporaryAccount(client)
        bidder = getTemporaryAccount(client)

        return Response(data={
            'creator_address':creator.getAddress(),
            'seller_address':seller.getAddress(),
            'bidder_address':bidder.getAddress(),
            'creator_sk':creator.getPrivateKey(),
            'seller_sk':seller.getPrivateKey(),
            'bidder_sk':bidder.getPrivateKey(),
        },status=status.HTTP_200_OK)

        