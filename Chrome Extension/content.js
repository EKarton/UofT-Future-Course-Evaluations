const COURSE_CODE_REGEX = /[A-Z][A-Z][A-Z]\d\d\d[A-Z]\d/g;

function getRatings(courseCode, abbrevInstructorName) {
    return new Promise(async (resolve, reject) => {
        let urlEncodedName = encodeURI(abbrevInstructorName);
        let baseUrl = 'http://0.0.0.0:5000/api/evals/future'
        let url = `${baseUrl}?course=${courseCode}&abbrev_instructor=${urlEncodedName}`;
        
        let xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);

        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200) {
                // JSON.parse does not evaluate the attacker's scripts.
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

window.onload = function () {
    // do the work after everything was loaded (DOM, media elements)
    console.log('loaded')
    addCssFile();
    console.log("loaded css file");
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
            
            // console.log(courseCode);

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

            // Show the ratings for the overall course
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

console.log('hehe')