select itm.Color color,
SUM(Total_SOH_Qty) Total_SOH_Qty,
SUM([SOH_Qty(30_Days)]) [30_Days],
SUM([SOH_Qty(60_Days)]) [60_Days],
SUM([SOH_Qty(90_Days)])	[90_Days]	,
SUM([SOH_Qty(180_Days)])	[180_Days]	,
SUM([SOH_Qty_(Above_181_Days)])	[Above_181_Days]	,
SUM([SOH_Qty(NON-GRN)])	[NON_GRN]
from lib_backup.dbo.olabi_stock_age soh
Left Join
	(Select * From libdata.dbo.item_master Where ean is not null and not parentStyleNo like 'test%'	) itm on itm.ean=soh.barcode
Left Join
	lib_backup.dbo.olabi_product_sku sk on sk.barcode = soh.barcode
where  sk.vendor_name LIKE '%SACHI%'
group by itm.Color