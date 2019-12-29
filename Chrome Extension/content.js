const COURSE_CODE_REGEX = /[A-Z][A-Z][A-Z]\d\d\d[A-Z]\d/g;
const EVALS_WEB_API_BASE_URL = 'http://0.0.0.0:5000/api/evals/future';

// TODO: Refactor this to handle bulk.
// Do something that is similar to CSC458: send the first request with courseCode and instructorName
// As it is being sent, any new requests will be queued.
// Then, once it is done, it will send all those that are queued in the next request.
var queuedRequests = [];
function getRatings(courseCode, abbrevInstructorName) {
    return new Promise(async (resolve, reject) => {
        let urlEncodedName = encodeURI(abbrevInstructorName);
        let url = `${EVALS_WEB_API_BASE_URL}?course=${courseCode}&abbrev_instructor=${urlEncodedName}`;
        
        let xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);

        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200) {
                let resp = JSON.parse(xhr.responseText);
                resolve(resp);
            }
        }
        xhr.onerror = function() {
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
    for (let i = 0; i < ratingElements.length; i++) {
        rootElement.appendChild(ratingElements[i]);
    }
}

function addCssFile() {
    var link = document.createElement("link");
    link.href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css";
    link.type = "text/css";
    link.rel = "stylesheet";
    document.getElementsByTagName("head")[0].appendChild(link);
}

function addRatingsControl() {
    // TODO: DOES NOT WORK!
    // let html = `
    // <div class="form-group filterBreadth" tabindex="0">
    //     <div id="tipBreadth" role="tooltip">Specify the course ratings to display</div>
    //     <label for="breadth" class="control-label">Course Ratings</label>
    //     <select id="breadth" multiple="multiple" class="form-control selectized" aria-describedby="tipBreadth" tabindex="-1" style="display: none;"></select>
    //     <div class="selectize-control form-control multi plugin-remove_button">
    //         <div class="selectize-input items not-full has-options">
    //             <input type="text" autocomplete="off" tabindex="" aria-labelledby="tipBreadth" aria-describedby="tipBreadth" style="width: 4px; opacity: 1; position: relative; left: 0px;"></div><div class="selectize-dropdown multi form-control plugin-remove_button" style="display: none; visibility: visible; width: 826px; top: 48px; left: 0px;">

    //             <div class="selectize-dropdown-content">
    //                 <div data-value="1" data-selectable="" class="option">Course intellectually stimulating (1)</div>
    //                 <div data-value="2" data-selectable="" class="option">Provided deeper understanding of the subject matter (2)</div>
    //                 <div data-value="3" data-selectable="" class="option">Learning Atmosphere (3)</div>
    //                 <div data-value="4" data-selectable="" class="option">Improved understanding of course content (4)</div>
    //                 <div data-value="5" data-selectable="" class="option">Fairness in test material (5)</div>
    //                 <div data-value="6" data-selectable="" class="option">Quality of learning experience (6)</div>
    //                 <div data-value="7" data-selectable="" class="option">Instructor generated enthusiasm (7)</div>
    //                 <div data-value="8" data-selectable="" class="option">Course Workload (8)</div>
    //                 <div data-value="9" data-selectable="" class="option">Course Recommendation (9)</div>
    //             </div>
    //         </div>
    //     </div>
    //     <div class="helper">
    //         Specify course ratings to display
    //     </div>
    // </div>
    // `;

    // document.querySelector('.secondary') .insertAdjacentHTML('beforeend', html);
}

window.onload = function () {
    addRatingsControl();
    addCssFile();

    MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

    // select the target node
    var target = document.getElementById('courses');

    // create an observer instance
    var observer = new MutationObserver(function (mutations, observer) {
        console.log(mutations, observer);

        // Going through all the courses
        let courseDivs = document.querySelectorAll('.perCourse');
        courseDivs.forEach(courseDiv => {
            let courseTitleTd = courseDiv.querySelector('.courseTitle');
            let courseCodeSpan = courseTitleTd.querySelector('.hiCC');
            let courseCode = courseCodeSpan.textContent.match(COURSE_CODE_REGEX);

            // Create a blank course ratings span
            let courseRatingSpan = document.createElement('span');
            courseRatingSpan.className += 'course-level-ratings';
            courseTitleTd.appendChild(courseRatingSpan);
            
            var maxRating = -1;

            // Going through all the instructors
            let instructorsTds = courseDiv.querySelectorAll('.colInst');
            console.log('instructorsTds.length:' + instructorsTds.length);
            instructorsTds.forEach((instructorsTd, instructorsTdIndex) => {
                let instructorsLi = instructorsTd.getElementsByTagName('li');
                
                console.log('instructorsTdIndex:' + instructorsTdIndex);
                console.log('instructorsLi.length:' + instructorsLi.length);

                Array.from(instructorsLi).forEach((instructorLi, instructorLiIndex) => {
                    let rawAbbrevInstructor = instructorLi.textContent;

                    let tokenizedName = rawAbbrevInstructor.split(',');
                    let lastName = tokenizedName[0]
                    let firstNameInitials = tokenizedName[1].substring(1, tokenizedName[1].length - 1);
                    let abbrevInstructor = `${lastName} ${firstNameInitials}`;

                    getRatings(courseCode, abbrevInstructor).then((ratings) => {
                        let concernedRating = ratings[8];
                        
                        if (concernedRating > maxRating) {
                            maxRating = concernedRating;
                            updateRatings(courseRatingSpan, maxRating);
                        }

                        let newNode = document.createElement('div');
                        newNode.appendChild(makeRatings(concernedRating));
                        instructorLi.appendChild(newNode);

                    }).catch(error => {
                        console.log(error);
                    });
                });
            });
        });
    });

    // configuration of the observer:
    var config = { 
        childList: true,
        characterData: true 
    };

    // pass in the target node, as well as the observer options
    observer.observe(target, config);
};
