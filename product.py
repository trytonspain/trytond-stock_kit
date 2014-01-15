#This file is part stock_kit module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Bool
import math

__all__ = ['Product']
__metaclass__ = PoolMeta
STATES = {
    'readonly': Bool(~Eval('kit')),
}
DEPENDS = ['kit']


class Product:
    __name__ = 'product.product'
    explode_kit_in_shipments = fields.Boolean('Explode in Shipments',
            states=STATES, depends=DEPENDS)
    stock_depends_on_kit_components = fields.Boolean('Stock Depends on '
            'Components', states=STATES, depends=DEPENDS,
            help='Indicates weather the stock of the current kit should'
                  ' depend on its components or not.')

    @staticmethod
    def default_explode_kit_in_shipments():
        return True

    @staticmethod
    def default_stock_depends_on_kit_components():
        return False

    def get_quantity(self, products, name):
        res = super(Product, self).get_quantity(products, name)
        #Calculate stock for kits that stock depends on sub-products
        for product in self.browse(products):
            if not product.stock_depends_on_kit_components or \
                not product.kit_lines:
                continue
            res[product.id] = 0.0
            subproducts_ids = [x.product.id for x in product.kit_lines]
            subproducts_stock = super(Product, self).get_quantity(
                subproducts_ids, name)
            pack_stock = False
            for subproduct in product.kit_lines:
                sub_qty = subproduct.quantity
                sub_stock = subproducts_stock.get(subproduct.product.id, 0)
                if not pack_stock:
                    pack_stock = math.floor(sub_stock / sub_qty)
                else:
                    pack_stock = min(pack_stock,
                                     math.floor(sub_stock / sub_qty))
            res[product.id] = pack_stock
        return res
