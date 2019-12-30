'use strict';

function onUpdateButtonClick() {
    let selectedRatingOptions = document.getElementById('selected-rating-options');
    let orderingOptions = document.getElementById('ordering-options');

    var message = { 
        operation: "reorder-ratings", 
        selectedRating: parseInt(selectedRatingOptions.options[selectedRatingOptions.selectedIndex].value),
        order: parseInt(orderingOptions.options[orderingOptions.selectedIndex].value)
    };

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, message, function(response) {
            console.log(response);
        });
    });
}

document.getElementById('view-different-ratings').addEventListener('click', onUpdateButtonClick);