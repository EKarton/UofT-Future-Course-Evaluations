'use strict';

function onUpdateButtonClick() {
    let viewRatingCheckboxes = document.querySelectorAll('.course-rating-checkbox');
    let orderingOptions = document.getElementById('ordering-options');

    let visibleRatings = [false, false, false, false, false, false, false, false, false];
    for (let i = 0; i < viewRatingCheckboxes.length; i++) {
        let checkbox = viewRatingCheckboxes[i];
        let index = parseInt(checkbox.getAttribute('value'));
        visibleRatings[index] = checkbox.checked;
    }

    var message = {
        visibleRatings: visibleRatings,
        sortBy: parseInt(orderingOptions.options[orderingOptions.selectedIndex].value)
    };

    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, message, function (response) {
            console.log(response);
        });
    });
}

document.body.onload = function () {
    document.getElementById('update-button').addEventListener('click', onUpdateButtonClick);
}