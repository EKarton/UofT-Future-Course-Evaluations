const COURSE_CODE_REGEX = /[A-Z][A-Z][A-Z]\d\d\d[A-Z]\d/g;
const EVALS_WEB_API_BASE_URL = 'http://0.0.0.0:5000/api/evals/future';

var globalSelectedRating = 8;

function getRatings(courseCode, abbrevInstructorName) {
    return new Promise(async (resolve, reject) => {
        let urlEncodedName = encodeURI(abbrevInstructorName);
        let url = `${EVALS_WEB_API_BASE_URL}?course=${courseCode}&abbrev_instructor=${urlEncodedName}`;

        let xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);

        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                let resp = JSON.parse(xhr.responseText);
                resolve(resp);
            }
        }
        xhr.onerror = function () {
            reject();
        }

        xhr.send();
    });
}

function getRatingElements(rating) {
    let roundedRating = Math.round(rating);
    let numStars = roundedRating;
    let numUncheckedStars = 5 - numStars;

    let ratingElements = [];

    for (let i = 0; i < numStars; i++) {
        let spanElement = document.createElement('span');
        spanElement.className = 'fa fa-star checked';
        ratingElements.push(spanElement);
    }
    for (let i = 0; i < numUncheckedStars; i++) {
        let spanElement = document.createElement('span');
        spanElement.className = 'fa fa-star';
        ratingElements.push(spanElement);
    }

    return ratingElements;
}

function makeRatings(rating) {
    let newNode = document.createElement('span');
    newNode.className += ' ratings';
    let ratingElements = getRatingElements(rating);
    for (let i = 0; i < ratingElements.length; i++) {
        newNode.appendChild(ratingElements[i]);
    }

    return newNode;
}

function updateRatings(rootElement, rating) {
    // Delete all the fa-star elements
    let elementsToDelete = rootElement.querySelectorAll('.fa-star');
    for (let i = 0; i < elementsToDelete.length; i++) {
        rootElement.removeChild(elementsToDelete[i]);
    }

    // Add back the fa-star elements
    let ratingElements = getRatingElements(rating);
    rootElement.className += ' ratings';
    for (let i = 0; i < ratingElements.length; i++) {
        rootElement.appendChild(ratingElements[i]);
    }
}

function setRatingsOnHtmlElement(htmlElement, ratings) {
    htmlElement.setAttribute('data-ratings', ratings);
}

function getRatingsOnHtmlElement(htmlElement) {
    let rawAttribute = htmlElement.getAttribute('data-ratings');

    let attributes = null;
    if (rawAttribute) {
        attributes = rawAttribute.split(',').map(item => parseFloat(item));
    }
    return attributes;
}

function arrayMax(arr1, arr2) {
    if (arr1.length != arr2.length) {
        throw Error('array lengths dont match!');
    }

    let newArray = [];
    for (let i = 0; i < arr1.length; i++) {
        newArray.push(Math.max(arr1[i], arr2[i]));
    }

    return newArray;
}

function updateRatingsOnAllCourses() {
    // Delete all existing ratings
    document.querySelectorAll('.ratings').forEach(item => item.parentElement.removeChild(item));

    // Going through all the courses
    let courseDivs = document.querySelectorAll('.courseResults');
    courseDivs.forEach(courseDiv => {
        let courseTitleTd = courseDiv.querySelector('.courseTitle');
        let courseCodeSpan = courseTitleTd.querySelector('.hiCC');
        let courseCode = courseCodeSpan.textContent.match(COURSE_CODE_REGEX);

        // Create a blank course ratings span
        let courseRatingSpan = document.createElement('span');
        courseRatingSpan.className += 'course-level-ratings';
        courseTitleTd.appendChild(courseRatingSpan);

        var courseRatings = [-1, -1, -1, -1, -1, -1, -1, -1, -1];

        // Going through all the instructors
        let instructorsTds = courseDiv.querySelectorAll('.colInst');
        // console.log('instructorsTds.length:' + instructorsTds.length);
        instructorsTds.forEach((instructorsTd, instructorsTdIndex) => {
            let instructorsLi = instructorsTd.getElementsByTagName('li');

            // console.log('instructorsTdIndex:' + instructorsTdIndex);
            // console.log('instructorsLi.length:' + instructorsLi.length);

            Array.from(instructorsLi).forEach((instructorLi, instructorLiIndex) => {
                let rawAbbrevInstructor = instructorLi.textContent;

                let tokenizedName = rawAbbrevInstructor.split(',');
                let lastName = tokenizedName[0]
                let firstNameInitials = tokenizedName[1].substring(1, tokenizedName[1].length - 1);
                let abbrevInstructor = `${lastName} ${firstNameInitials}`;

                let existingRating = getRatingsOnHtmlElement(instructorLi);
                if (existingRating != null) {

                    nextCourseRatings = arrayMax(existingRating, courseRatings)
        
                    if (nextCourseRatings != courseRatings) {
                        courseRatings = nextCourseRatings;
                        updateRatings(courseRatingSpan, courseRatings[globalSelectedRating]);
                        setRatingsOnHtmlElement(courseDiv, courseRatings);
                    }

                    let newNode = document.createElement('div');
                    newNode.appendChild(makeRatings(existingRating[globalSelectedRating]));
                    instructorLi.appendChild(newNode);

                } else {
                    getRatings(courseCode, abbrevInstructor).then((ratings) => {

                        nextCourseRatings = arrayMax(ratings, courseRatings)
        
                        if (nextCourseRatings != courseRatings) {
                            courseRatings = nextCourseRatings;
                            updateRatings(courseRatingSpan, courseRatings[globalSelectedRating]);
                            setRatingsOnHtmlElement(courseDiv, courseRatings);
                        }
    
                        setRatingsOnHtmlElement(instructorLi, ratings);
                        let newNode = document.createElement('div');
                        newNode.appendChild(makeRatings(ratings[globalSelectedRating]));
                        instructorLi.appendChild(newNode);
    
                    }).catch(error => {
                        // console.log(error);
                    });
                }
            });
        });
    });
}

function addCssFile() {
    var link = document.createElement("link");
    link.href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css";
    link.type = "text/css";
    link.rel = "stylesheet";
    document.getElementsByTagName("head")[0].appendChild(link);
}

var target = null;
var observer = null

function startObserving() {
    MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

    // select the target node
    target = document.getElementById('courses');

    // create an observer instance
    observer = new MutationObserver(function (mutations, observer) {
        // console.log(mutations, observer);
        updateRatingsOnAllCourses();
    });

    // configuration of the observer:
    var config = {
        childList: true,
        characterData: true
    };

    // pass in the target node, as well as the observer options
    observer.observe(target, config);
}

function stopObserving() {
    if (observer != null) {
        observer.disconnect();
    }
}

window.onload = function () {
    addCssFile();
    startObserving();
};

/**
 * Sorts the ordering of courses based on ratings
 * @param {Integer} selectedRatings The selected ratings (either -1, 0, 1, 2, ..., 8)
 * @param {Integer} order The ordering of the courses (either -1, 0, or 1)
 */
function updateCourseRatings(selectedRatings, order) {
    stopObserving();
    var coursesDiv = document.getElementById("courses");

    [].slice.call(coursesDiv.children)
        .sort((courseA, courseB) => {

            // If ratings determine the ordering
            if (order == 0) {
                return 1;

            } else {
                let courseARatings = getRatingsOnHtmlElement(courseA);
                let courseBRatings = getRatingsOnHtmlElement(courseB);
                console.log(courseA);
                console.log(courseB);

                if (courseARatings == null || courseBRatings == null) {
                    return -1;
                }
                
                let selectedCourseARating = courseARatings[selectedRatings];
                let selectedCourseBRating = courseBRatings[selectedRatings];

                if (selectedCourseARating == selectedCourseBRating) {
                    return 0;
                }

                if (order == -1) {
                    return selectedCourseARating < selectedCourseBRating ? -1 : 1;

                } else if (order == 1) {
                    return selectedCourseARating > selectedCourseBRating ? -1 : 1;

                }
            }
        })
        .map(node => coursesDiv.appendChild(node));
    startObserving();
    updateRatingsOnAllCourses();
}

chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        let operation = request.operation;
        let selectedRating = request.selectedRating;
        let order = request.order;

        globalSelectedRating = selectedRating;

        switch (operation) {
            case "reorder-ratings":
                updateCourseRatings(selectedRating, order);
                sendResponse({ status: "ok" });
                break;

            default:
                throw Error("Unknown operation:", operation);
        }            
    });