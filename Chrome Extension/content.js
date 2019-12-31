'use strict';

(() => {
    const COURSE_CODE_REGEX = /[A-Z][A-Z][A-Z]\d\d\d[A-Z]\d/g;
    const RATING_DETAILS = [
        'Intellectually stimulating',
        'Usefulness',
        'Learning athmosphere',
        'Improved understanding of course content',
        'Fairness in test material',
        'Quality of learning experience',
        'Instructor generated enthusiasm',
        'Course Workload',
        'Course Recommendation'
    ];

    var ratingVisibility = [true, true, false, false, false, false, false, true, true];
    var observer = null;

    function getRatingElements(rating) {
        let roundedRating = Math.round(rating);
        let numStars = roundedRating;
        let numUncheckedStars = 5 - numStars;

        let ratingElements = [];

        for (let i = 0; i < numStars; i++) {
            let spanElement = document.createElement('span');
            spanElement.className = 'fas fa-star fa-xs checked';
            ratingElements.push(spanElement);
        }
        for (let i = 0; i < numUncheckedStars; i++) {
            let spanElement = document.createElement('span');
            spanElement.className = 'fas fa-star fa-xs';
            ratingElements.push(spanElement);
        }

        return ratingElements;
    }

    function saveRatingsToHtmlElement(htmlElement, ratings) {
        htmlElement.setAttribute('data-ratings', ratings);
    }

    function loadRatingsFromHtmlElement(htmlElement) {
        let rawVal = htmlElement.getAttribute('data-ratings');

        if (rawVal) {
            return rawVal.split(',').map(item => parseFloat(item));
        }
        return null;
    }

    function getCourseCodesAndInstructorsOnPage() {
        let courseCodes = [];
        let abbrevInstructors = [];

        let courseDivs = document.querySelectorAll('.courseResults');
        for (let i = 0; i < courseDivs.length; i++) {
            let courseDiv = courseDivs[i];
            let courseTitleTd = courseDiv.querySelector('.courseTitle');
            let courseCodeSpan = courseTitleTd.querySelector('.hiCC');
            let courseCode = courseCodeSpan.textContent.match(COURSE_CODE_REGEX);

            let instructorsTds = courseDiv.querySelectorAll('.colInst');
            for (let j = 0; j < instructorsTds.length; j++) {
                let instructorsLi = instructorsTds[j].getElementsByTagName('li');
                
                for (let k = 0; k < instructorsLi.length; k++) {
                    let instructorLi = instructorsLi[k];
                    let rawAbbrevInstructor = instructorLi.textContent;

                    let tokenizedName = rawAbbrevInstructor.split(',');
                    let lastName = tokenizedName[0]
                    let firstNameInitials = tokenizedName[1].substring(1, tokenizedName[1].length - 1);
                    let abbrevInstructor = `${lastName} ${firstNameInitials}`;

                    courseCodes.push(courseCode);
                    abbrevInstructors.push(abbrevInstructor);
                }
            }
        }

        return {
            courseCodes: courseCodes,
            abbrevInstructors: abbrevInstructors
        };
    }

    function addSpinners() {
        // Going through all the courses
        let courseDivs = document.querySelectorAll('.courseResults');
        courseDivs.forEach(courseDiv => {

            // Show a spinner while the ratings are being fetched
            let spinnerElementContainer = document.createElement('div');
            spinnerElementContainer.className = 'spinner-container';

            let spinnerElement = document.createElement('span');
            spinnerElement.className = 'spinner';

            let spinnerElementText = document.createElement('span');
            spinnerElementText.textContent = 'Loading ratings...';
            spinnerElementText.className = 'spinner-text';

            spinnerElementContainer.appendChild(spinnerElement);
            spinnerElementContainer.appendChild(spinnerElementText);

            let courseTitleTd = courseDiv.querySelector('.courseTitle');
            courseTitleTd.appendChild(spinnerElementContainer);
        });
    }

    function removeSpinners() {
        // Going through all the courses
        let courseDivs = document.querySelectorAll('.courseResults');
        courseDivs.forEach(courseDiv => {
            let courseTitleTd = courseDiv.querySelector('.courseTitle');
            courseTitleTd.removeChild(courseTitleTd.querySelector('.spinner-container'));
        });
    }

    function updateRatingsOnAllCourseDivs(ratings) {
        // Delete all existing ratings
        document.querySelectorAll('.ratings').forEach(item => item.parentElement.removeChild(item));

        // Going through all the courses
        let courseDivs = document.querySelectorAll('.courseResults');
        courseDivs.forEach(courseDiv => {

            let courseTitleTd = courseDiv.querySelector('.courseTitle');
            let courseCodeSpan = courseTitleTd.querySelector('.hiCC');
            let courseCode = courseCodeSpan.textContent.match(COURSE_CODE_REGEX);

            // The course average
            var courseRatings = [0, 0, 0, 0, 0, 0, 0, 0, 0];
            var numRatings = 0;

            // Going through all the instructors
            let instructorsTds = courseDiv.querySelectorAll('.colInst');
            for (let i = 0; i < instructorsTds.length; i++) {
                let instructorsLi = instructorsTds[i].getElementsByTagName('li');
                
                for (let j = 0; j < instructorsLi.length; j++) {
                    let instructorLi = instructorsLi[j];
                    let rawAbbrevInstructor = instructorLi.textContent;

                    let tokenizedName = rawAbbrevInstructor.split(',');
                    let lastName = tokenizedName[0]
                    let firstNameInitials = tokenizedName[1].substring(1, tokenizedName[1].length - 1);
                    let abbrevInstructor = `${lastName} ${firstNameInitials}`;

                    let key = courseCode + '|' + abbrevInstructor;
                    if (key in ratings) {
                        courseRatings = Utils.arrayAdd(courseRatings, ratings[key]);
                        numRatings += 1;
                    }
                }
            }

            // Show the course averages
            if (numRatings > 0) {

                // Update the avg course rating
                courseRatings = Utils.arrayDivide(courseRatings, numRatings);

                // Save the ratings to the HTML element for sorting
                saveRatingsToHtmlElement(courseDiv, courseRatings);

                // A wrapper div for all of our ratings
                let courseRatingsWrapper = document.createElement('div');
                
                for (let i = 0; i < courseRatings.length; i++) {
                    let ratingElement = document.createElement('div');
                    ratingElement.className = "rating";
                    ratingElement.setAttribute('data-rating-category', i);

                    let ratingParts = getRatingElements(courseRatings[i]);
                    for (let j = 0; j < ratingParts.length; j++) {
                        ratingElement.appendChild(ratingParts[j]);
                    }

                    let ratingText = document.createElement('span');
                    ratingText.className = 'rating-text';
                    ratingText.textContent = '  ' +  courseRatings[i].toFixed(2) + '  ' + RATING_DETAILS[i];
                    ratingElement.appendChild(ratingText);

                    courseRatingsWrapper.appendChild(ratingElement);

                    // Set its visibility based on ratingVisibility
                    if (ratingVisibility[i]) {
                        ratingElement.style.display = 'block';

                    } else {
                        ratingElement.style.display = 'none';
                    }
                }

                courseTitleTd.appendChild(courseRatingsWrapper);
            }
        });
    }

    function updateRatingsOnAllCourses() {
        addSpinners();

        let courseDetails = getCourseCodesAndInstructorsOnPage();
        EvalsApi.getRatings(courseDetails['courseCodes'], courseDetails['abbrevInstructors'])
            .then(ratings => {
                removeSpinners();
                updateRatingsOnAllCourseDivs(ratings);
            })
            .catch(error => {
                console.error(error);
                removeSpinners();
            });
    }

    function startObserving() {
        if (observer !== null) {
            observer.disconnect();
        }

        MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

        let target = document.getElementById('courses');

        var config = {
            childList: true,
            characterData: true
        };

        observer = new MutationObserver(function (mutations, observer) {
            updateRatingsOnAllCourses();
        });
        observer.observe(target, config);
    }

    function stopObserving() {
        if (observer != null) {
            observer.disconnect();
        }
    }

    function updateCourseRatingsVisibility(visibleRatings) {
        stopObserving();

        // Toggle on/off visibility on all ratings
        let ratingElements = document.querySelectorAll('.rating');
        for (let i = 0; i < ratingElements.length; i++) {
            let ratingElement = ratingElements[i];
            let ratingCategory = parseInt(ratingElement.getAttribute('data-rating-category'));

            if (visibleRatings[ratingCategory]) {
                ratingElement.style.display = "block";

            } else {
                ratingElement.style.display = "none";
            }
        }
        startObserving();
    }

    function sortCourseListing(sortBy) {
        stopObserving();

        // Sort the courses
        if (sortBy >= 0) {
            var rootCourseDiv = document.getElementById("courses");
            var courseDivs = Array.prototype.slice.call(rootCourseDiv.children);

            console.log(courseDivs.length);

            // Take the courses with ratings
            let courseDivsWithRatings = courseDivs.filter(courseDiv => loadRatingsFromHtmlElement(courseDiv) !== null);

            // Take the courses with no ratings
            let courseDivsWithNoRatings = courseDivs.filter(courseDiv => loadRatingsFromHtmlElement(courseDiv) === null);

            // Remove all courses
            while (rootCourseDiv.firstChild) {
                rootCourseDiv.removeChild(rootCourseDiv.firstChild);
            }

            // Sort the courses with ratings
            courseDivsWithRatings = courseDivsWithRatings.sort((courseA, courseB) => {
                let courseARatings = loadRatingsFromHtmlElement(courseA);
                let courseBRatings = loadRatingsFromHtmlElement(courseB);
                
                let selectedCourseARating = courseARatings[sortBy];
                let selectedCourseBRating = courseBRatings[sortBy];

                if (selectedCourseARating < selectedCourseBRating) {
                    return -1;
                    
                } else if (selectedCourseARating == selectedCourseBRating) {
                    return 0;

                } else {
                    return 1;
                }
            });

            // Add back the courses with ratings
            for (let i = 0; i < courseDivsWithRatings.length; i++) {
                rootCourseDiv.append(courseDivsWithRatings[i]);
            }

            // Add back the courses with no ratings
            for (let i = 0; i < courseDivsWithNoRatings.length; i++) {
                rootCourseDiv.append(courseDivsWithNoRatings[i]);
            }
        }
        
        startObserving();
    }

    window.onload = function () {
        // Add a custom CSS file
        var link = document.createElement("link");
        link.href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.min.css";
        link.type = "text/css";
        link.rel = "stylesheet";
        document.getElementsByTagName("head")[0].appendChild(link);

        // Start observing changes to the DOM
        startObserving();
    }

    chrome.runtime.onMessage.addListener(
        function (request, sender, sendResponse) {
            let visibleRatings = request.visibleRatings;
            let sortBy = request.sortBy;

            ratingVisibility = visibleRatings;

            updateCourseRatingsVisibility(visibleRatings);
            sortCourseListing(sortBy);

            sendResponse({ status: "ok" });         
        });
})();