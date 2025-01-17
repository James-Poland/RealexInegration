﻿Create Proc [Payments].[AddCard] @claimnumber varchar(50)
as 
Begin
Set NoCount on;

OPEN SYMMETRIC KEY CreditCards_Key
	DECRYPTION BY CERTIFICATE DebtCC

IF object_id('tempdb.dbo.#NewCard', 'U') IS NOT NULL
		DROP TABLE #NewCard;

SELECT    top 1  ClaimNumber, Currency, CardName, m.PAYERREF,m.paymentref,
case when t.CARDTYPE = 'mastercard' then 'MC' else upper(t.CardType) end as
		CardType,
CONVERT(varchar, DecryptByKey(c.cardnumber))CardNumber, 
Expiry, CVV, CustToken, CardToken, m.MigStatus
into #NewCard 
FROM            dbo.CardDetails c
inner join 
CardType t on c.CardType=t.ID
left join Payments.Migration m on left(replace(PAYMENTREF,'*',' '), charindex('_', replace(PAYMENTREF,'*',' ')) -1)=c.ClaimNumber
where 
dbo.fnIsValidCard(CONVERT(varchar, DecryptByKey(c.cardnumber)))=1
and ClaimNumber=@claimnumber


Declare @timestamp varchar(50)
Declare @orderid varchar(50)
Declare @payref varchar(50)
declare @ref varchar(50)
Declare @cardname varchar(50)
Declare @Cardnum varchar(50)
Declare @hash1 varchar(100)
declare @hash2 varchar (100)
declare @cardref varchar(50)
set @payref = (Select payerref from #newcard) 
set @cardname = (select CardName from #newcard)
set @Cardnum = (select cardnumber from #newcard)
set @cardref = (Select replace(paymentref,' ','')paymentref from #newcard)
set @timestamp =convert(varchar(20),CURRENT_TIMESTAMP,112)+replace(convert(varchar, getdate(), 8),':','')
set @orderid =replace(NewID(),'-','')
set @hash1 = (select top 1 SUBSTRING(master.dbo.fn_varbintohexstr(hashbytes('sha1',(Select @timestamp+'.'+'Client'+'.'+@orderid+'...'+@payref+'.'+@cardname+'.'+@Cardnum ))),3,40))
set @hash2 = @hash1+'.'+'Pass'
declare @msg xml

set @msg =(
Select top 1
'card-new' as "@type" ,@timestamp as "@timestamp" ,
'Client' as merchantid,
@orderid as orderid,
(
Select @cardref as ref,
@payref as payerref, 
@Cardnum as number, Expiry as expdate,
	CardName as chname,CardType as [type]
	for xml path ('card'),type),
	SUBSTRING(master.dbo.fn_varbintohexstr(hashbytes('sha1',(select @hash1+'.'+'Pass'))),3,128) as sha1hash
	from #newcard
FOR XML PATH('request')
)

select @msg

Insert into Payments.CardRequests
Select @cardref, @orderid, 'card-new' as MsgType,getdate() as MsgDate,NULL, @msg 
from #newcard
where not exists 
(select r.Payerref
from
Payments.CardRequests r
where payerref = @payref and MsgType = 'card-new'
							   )
update c
set c.CustToken = @payref, c.CardToken = @cardref,
SafeCardNo = 'XXXX-XXXX-XXXX- '+right(CONVERT(varchar, n.cardnumber),4)
from dbo.CardDetails c 
inner join #newcard n
on c.ClaimNumber=n.ClaimNumber


update Payments.Migration
set MigStatus ='CardSent'
where payerref= @payref

Close SYMMETRIC KEY CreditCards_Key


end
