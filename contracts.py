from pyteal import *

def approval_program():
    seller_key = Bytes("seller")
    nft_id_key = Bytes("nft_id")
    start_time_key = Bytes("start")
    end_time_key = Bytes("end")
    reserve_amount_key = Bytes("reserve_amount")
    min_bid_increment_key = Bytes("min_bid_inc")
    num_bids_key = Bytes("num_bids")
    lead_bid_amount_key = Bytes("bid_amount")
    lead_bid_account_key = Bytes("bid_account")

    @Subroutine(TealType.none)
    def closeNFTTo(assetID: Expr,account:Expr)->Expr:
        asset_holding = AssetHolding.balance(
            Global.current_application_address(),assetID
        )
        return Seq(
            asset_holding,
            If(asset_holding.hasValue()).Then(
                Seq(
                    InnerTxnBuilder.Begin(),
                    InnerTxnBuilder.SetFields(
                        {
                            TxnField.type_enum: TxnType.AssetTransfer,
                            TxnField.xfer_asset: assetID,
                            TxnField.asset_close_to: account
                        }
                    ),
                    InnerTxnBuilder.Submit(),
                )
            ),
        )

    @Subroutine(TealType.none)
    def repayPreviousLeadBidder(prevLeadBidder: Expr, prevLeadBidAmount: Expr)->Expr:
        return Seq(
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields(
                {
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.amount: prevLeadBidAmount  - Global.min_txn_fee(),
                    TxnField.receiver: prevLeadBidder
                }
            )
        )

    @Subroutine(TealType.none)
    def closeAccountTo(account:Expr)->Expr:
        return If(Balance(Global.current_application_address())!=Int(0)).Then(
            Seq(
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum:TxnType.Payment,
                    TxnField.close_remainder_to: account
                }),
                InnerTxnBuilder.Submit(),
            )
        )




