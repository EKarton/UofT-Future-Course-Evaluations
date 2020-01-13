
var EvalsApi = {
    
    /**
     * Fetches the ratings of each pair of courses and instructors using the bulk API
     * @param {List<String>} courseCodes list of course codes
     * @param {List<String>} abbrevInstructorNames list of abbrev. instructor names
     */
    getRatings: function (courseCodes, abbrevInstructorNames) {
        const EVALS_BULK_WEB_API_BASE_URL = 'https://uoft-project.herokuapp.com/api/v2/bulk/evals/future';

        return new Promise((resolve, reject) => {

            console.log(courseCodes);
            
            let xhr = new XMLHttpRequest();
            let requestBody = JSON.stringify({courses: courseCodes, abbrev_instructors: abbrevInstructorNames});

            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4) {
                    if (xhr.status == 200) {

                        let responses = JSON.parse(xhr.responseText);

                        let parsedRatings = {};
                        for (let i = 0; i < responses.length; i++) {
                            let response = responses[i];
                            let courseCode = response['course'];
                            let instructor = response['instructor']
                            let status = response['status'];

                            if (status === "ok") {
                                let ratings = response['ratings'];
                                parsedRatings[courseCode + '|' + instructor] = ratings;
                            }
                        }

                        resolve(parsedRatings);

                    } else {
                        reject({
                            status: xhr.status,
                            statusText: xhr.statusText
                        });
                    }
                }
            }
            xhr.onerror = function () {
                reject();
            }

            xhr.open('POST', EVALS_BULK_WEB_API_BASE_URL, true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.send(requestBody);
        });
    }
};