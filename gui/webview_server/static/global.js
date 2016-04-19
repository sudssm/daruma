"use strict";

/********************
 * Slider functions *
 ********************/
function goToSlide(slideContainerId, slideNo) {
    $(slideContainerId).css("margin-left", (-100 * slideNo) + "%");
}
