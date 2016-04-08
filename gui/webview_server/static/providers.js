"use strict";

function onAddProviderButtonClick() {
    goToSlide("#add-provider-slide-container", 0);
    showModalById("#add-provider-modal");
}

function onAddProviderCancel() {
    hideModalById("#add-provider-modal");
}
