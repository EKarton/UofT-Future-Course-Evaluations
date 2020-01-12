
var EvalsApi = {
    
    /**
     * Fetches the ratings of each pair of courses and instructors using the bulk API
     * @param {List<String>} courseCodes list of course codes
     * @param {List<String>} abbrevInstructorNames list of abbrev. instructor names
     */
    getRatings: function (courseCodes, abbrevInstructorNames) {
        const EVALS_BULK_WEB_API_BASE_URL = 'https://uoft-project.herokuapp.com/api/bulk/evals/future';

        return new Promise((resolve, reject) => {
            let courseCodesQueryStringParam = '';
            for (let i = 0; i < courseCodes.length; i++) {
                courseCodesQueryStringParam += courseCodes[i] + ','
            }

            if (courseCodesQueryStringParam.length > 0) {
                courseCodesQueryStringParam = courseCodesQueryStringParam.substring(0, courseCodesQueryStringParam.length - 1);
            }

            let instQueryStringParam = '';
            for (let i = 0; i < abbrevInstructorNames.length; i++) {
                instQueryStringParam += encodeURI(abbrevInstructorNames[i]) + ','
            }

            if (instQueryStringParam.length > 0) {
                instQueryStringParam = instQueryStringParam.substring(0, instQueryStringParam.length - 1);
            }

            let url = `${EVALS_BULK_WEB_API_BASE_URL}?courses=${courseCodesQueryStringParam}&abbrev_instructors=${instQueryStringParam}`;

            let xhr = new XMLHttpRequest();

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

            xhr.open('GET', url, true);
            xhr.send();
        });
    }
};