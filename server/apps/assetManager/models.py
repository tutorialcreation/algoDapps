from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Nft(models.Model):
    nft_id = models.IntegerField(null=True,blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    address = models.CharField(max_length=255,null=True,blank=True)
    sk = models.CharField(max_length=255,null=True,blank=True)
    role = models.ForeignKey(Group,on_delete=models.CASCADE,null=True,blank=True)
    amount = models.IntegerField(null=True,blank=True)
    is_bidder = models.BooleanField(default=False)


class Asset(models.Model):
    nft = models.ForeignKey(Nft,on_delete=models.CASCADE,null=True,blank=True,related_name="nftHolder")
    unit_name = models.CharField(max_length=10,null=True,blank=True)
    asset_name = models.CharField(max_length=255,null=True,blank=True)
    asset_url = models.URLField(null=True,blank=True)
    note = models.TextField(null=True,blank=True)
    is_bidded = models.BooleanField(default=False)
    bidders = models.ManyToManyField(Nft)
    


class Application(models.Model):
    app_id = models.IntegerField(null=True,blank=True)
    app_nft = models.ForeignKey(Nft,on_delete=models.CASCADE,null=True,blank=True)
    start_time = models.IntegerField(null=True,blank=True)
    end_time = models.IntegerField(null=True,blank=True)
    

    def __str__(self) -> str:
        return str(self.app_id)