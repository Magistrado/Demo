#
#   Creator: Daniel Leones
#   Description: Extract categories and products from JSON files by using DFS algorithm. This prints to stdout.
#               the results on Oscar hierarchy notation
#
#   Data: 7/12/2017
#   Modified : 27/04/2018

from file_handler import FileHandler
from django.db import transaction
from db_handler import DBAccess
from decimal import Decimal as D


###############################################################################

def nav_prods(json_products, bre_cat, db_oscar):
    """
    Creates  products inside a JSON file and load them into the DB
    Return processed product number
    """
    def get_successors(child):
        products = child.get('products')
        if products:
            return products

        products = child.get('replacements')
        if products:
            return products

        return None

    comp_img = json_products.get('image')
    cat = db_oscar.create_category(bre_cat, comp_img)

    stack = list()
    stack.append((json_products, None))
    product_num = 0

    while stack:
        prod_json, parent = stack.pop()
        successors = get_successors(prod_json)

        pro = None
        prod_name = prod_json.get('product')
        if prod_name:
            is_available = prod_json.get('is_available')
            part_number_v = prod_json.get('part_number')
            manufacturer_v = prod_json.get('manufacturer')
            diagram_number_v = prod_json.get('diagram_number')
            price_excl_tax = prod_json.get('price', '0.00')
            cost_price = prod_json.get('cost_price', '0.00')
            price_retail = prod_json.get('price_retail', '0.00')
            origin_v = prod_json.get('origin')

            prod, exists = db_oscar.check_partnumber(part_number_v)
            if exists:
                db_oscar.add_product_to_category(prod, cat, diagram_number_v)
                if parent:
                    db_oscar.asign_prod_replacement(parent, prod)
            else:
                pro = db_oscar.create_prods(cat, is_available, prod_name,
                                            part_number_v, manufacturer_v,
                                            origin_v, diagram_number_v,
                                            price_excl_tax, price_retail,
                                            cost_price)
                db_oscar.add_part_number(part_number_v)
                product_num += 1

                if parent:
                    db_oscar.asign_prod_replacement(parent, pro)

        if successors:
            for suc in successors:
                stack.append((suc, pro))

    return product_num

########################################################################################################################


def get_sucessors(child):
    suc_cat = child.get('categories')
    if suc_cat:
        return suc_cat

    suc_sub_cat = child.get('sub_category')
    if suc_sub_cat:
        return suc_sub_cat

    return None


def get_names(child):
    sucs_nom = child.get('category')
    if sucs_nom:
        return sucs_nom
    else:
        return ''


@transaction.atomic
def extract_prods(categories_json, db):
    stack = list()
    stack.append((categories_json, ''))
    path = list()
    products_num = 0

    while stack:
        child, _ = stack.pop()
        successors = get_sucessors(child)
        child_name = get_names(child).strip()
        path.append(child_name)

        if successors:
            for suc in successors:
                stack.append((suc, child_name))
        else:
            products_num += nav_prods(child, list(path), db)

            if stack:
                _, parent = stack[-1]
                while path[-1] != parent:
                    path.pop()

    return products_num


def extract_cats(category_json):
    """
    :param category_json: JSON object
    :return: A nested list of categories
    """
    stack = list()
    stack.append((category_json, ''))
    categories = list()
    path = list()

    while stack:
        child, _ = stack.pop()
        successors = get_sucessors(child)
        child_name = get_names(child).strip()
        path.append(child_name)

        if successors:
            for suc in successors:
                stack.append((suc, child_name))
        else:
            # Add or create categories
            categories.append(list(path))

            if stack:
                _, parent = stack[-1]
                while path[-1] != parent:
                    path.pop()

    categories.reverse()
    return categories


def to_hierarchy_notation(list):
    xs = []
    for li in list:
        lit = ' > '.join(li[1:])
        xs.append(lit)

    return xs


def print_categories(categories):
    total = 0
    for cat in categories:
        print(cat)
        total += 1
    print('Categories found: %s' % total)

def exec_ext_categories(caminoArch):
    fh = FileHandler()
    exec_ext_categories_with(caminoArch, fh)

def exec_ext_categories_with(caminoArch, ioh):
    print_categories(to_hierarchy_notation(extract_cats(ioh.read(caminoArch))))

def exec_loader(path, base_cat, verbosity):
    fh = FileHandler()
    return extract_prods(fh.read(path), DBAccess(base_cat))
