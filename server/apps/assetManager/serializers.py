from rest_framework import serializers
from apps.assetManager.models import Nft,Asset

class AssetSerializer(serializers.ModelSerializer):
    nft_id = serializers.CharField(source='nft.nft_id')
    user = serializers.CharField(source='nft.user')
    address = serializers.CharField(source='nft.address')
    role = serializers.CharField(source='nft.role')
    amount = serializers.CharField(source='nft.amount')
    is_bidder = serializers.CharField(source='nft.is_bidder')
    application = serializers.CharField(source='nft.application_set.all')

    class Meta:
        model = Asset
        fields = (
            'id',
            'unit_name',
            'asset_name',
            'asset_url',
            'note',
            'is_bidded',
            'bidders',
            'nft_id',
            'user',
            'address',
            'role',
            'amount',
            'is_bidder',
            'application',
        )