from db_handler import DBAccess
from file_handler import ExcelHandler
from django.db import transaction


def exec_excel_load(path, cat, base_cate, manufac_name, origin_name):
    return excel_load(
        cat,
        DBAccess(base_cate),
        ExcelHandler().read(path),
        manufac_name,
        origin_name
    )


@transaction.atomic
def excel_load(cat, marine_parts_db, prods_ls, manufac_name, origin_name):
    num = 0
    cat = marine_parts_db.create_category(['', cat], None)

    for row in prods_ls:
        marine_parts_db.create_prods(
            cat, True, row['Name'], row['SKU'], manufac_name,
            origin_name, '', row['Price'], row['SalePrice'], row['Cost']
        )
        num += 1
    return num
