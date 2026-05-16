/** @odoo-module **/

import VariantMixin from "@website_sale/js/sale_variant_mixin";
import { patch } from "@web/core/utils/patch";

const _dasLmsOnChangeCombinationOrig = VariantMixin._onChangeCombination;

/**
 * Ocultar controles de compra cuando LMS así lo indica.
 * El mixin estándar de Odoo, tras variantes, hace siempre visible el carrito si no hay
 * prevent_zero_price_sale; por eso además usamos data-das-lms-hide-shop + SCSS !important.
 */
function dasLmsApplyCourseQtyFixed($parent, combination) {
    const quantity = $parent.find(".css_quantity");
    const qtyInput = quantity.find('input[name="add_qty"]').length
        ? quantity.find('input[name="add_qty"]')
        : quantity.find("input").first();
    const hideFromDom = Boolean($parent.closest('[data-das-lms-hide-shop="1"]').length);
    if (!quantity.length || hideFromDom) {
        return;
    }
    const fixed = Boolean(combination && combination.das_lms_course_qty_fixed);
    if (fixed) {
        quantity.removeClass("d-inline-flex").addClass("d-none");
        if (qtyInput.length) {
            qtyInput.val(1);
        }
        return;
    }
}

function dasLmsApplyShopVisibility($parent, combination) {
    const addToCart = $parent.find("#add_to_cart_wrap");
    const quantity = $parent.find(".css_quantity");
    const priceBox = $parent.find(".product_price");
    const hideFromPayload = Boolean(combination && combination.das_lms_hide_add_to_cart);
    const hideFromDom = Boolean($parent.closest('[data-das-lms-hide-shop="1"]').length);
    const hide = hideFromPayload || hideFromDom;
    const preventZero = Boolean(combination && combination.prevent_zero_price_sale);
    if (!addToCart.length) {
        return;
    }
    if (hide) {
        addToCart.removeClass("d-inline-flex").addClass("d-none");
        quantity.removeClass("d-inline-flex").addClass("d-none");
        priceBox.removeClass("d-inline-block").addClass("d-none");
        return;
    }
    if (combination && !preventZero) {
        addToCart.removeClass("d-none").addClass("d-inline-flex");
        quantity.removeClass("d-none").addClass("d-inline-flex");
        priceBox.removeClass("d-none").addClass("d-inline-block");
    }
}

patch(VariantMixin, {
    _onChangeCombination(ev, $parent, combination) {
        const res = _dasLmsOnChangeCombinationOrig.call(this, ev, $parent, combination);
        try {
            dasLmsApplyShopVisibility($parent, combination);
            dasLmsApplyCourseQtyFixed($parent, combination);
            queueMicrotask(() => {
                dasLmsApplyShopVisibility($parent, combination);
                dasLmsApplyCourseQtyFixed($parent, combination);
            });
        } catch (_e) {
            /* no romper la tienda si datos incompletos */
        }
        return res;
    },
});
