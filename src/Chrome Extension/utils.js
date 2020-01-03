var Utils = {
    arrayMax: function (arr1, arr2) {
        if (arr1.length != arr2.length) {
            throw Error('array lengths dont match!');
        }

        let newArray = [];
        for (let i = 0; i < arr1.length; i++) {
            newArray.push(Math.max(arr1[i], arr2[i]));
        }

        return newArray;
    },

    arrayAdd: function (arr1, arr2) {
        if (arr1.length != arr2.length) {
            throw Error('array lengths dont match!');
        }

        let newArray = [];
        for (let i = 0; i < arr1.length; i++) {
            newArray.push(arr1[i] + arr2[i]);
        }

        return newArray;
    },

    arrayDivide: function (arr1, num) {
        let newArray = [];
        for (let i = 0; i < arr1.length; i++) {
            newArray.push(arr1[i] / num);
        }

        return newArray;
    }
};