const BASE = "http://localhost:5000/api/v1.0/";

// Initialize Firebase
var config = {
    apiKey: "AIzaSyD5nk1FZgtBuMaUiZxVqd6tx3JjUCeRzVw",
    authDomain: "cs6460-183715.firebaseapp.com",
    databaseURL: "https://cs6460-183715.firebaseio.com",
    projectId: "cs6460-183715",
    storageBucket: "cs6460-183715.appspot.com",
    messagingSenderId: "844094396961"
};
firebase.initializeApp(config);

/**
 * @brief enroll user in system
 * @param uid LTS unique id
 * @param accessToken authorization token
 * @param callback function accepting bool true or false, true is success, false is error
 */
function enroll(uid, accessToken, callback) {

    scrapeCoursePageInfo(function(courseInfo) {
        $.ajax({
            url: BASE + 'enroll/' + uid,
            headers: {
                'Authorization': 'Bearer ' + accessToken,
                'cache-control': 'no-cache'
            },
            data: courseInfo,
            type: 'POST',
            success: function (data) {
                callback(true);
            },
            error: function (data) {
                callback(false);
            }
        });
    });
}

/**
 * @brief Fetch the stats of specified user
 * @param uid LTS unique id for user
 * @param accessToken authorization token to prevent impersonation
 * @param callback callback receives fetched data
 * @param err callback recieves raw ajax error
 */
function fetchStats(uid, accessToken, callback, err) {
    scrapeCoursePageInfo(function(courseInfo) {
        $.ajax({
            url: BASE + 'stats/' + uid,
            headers: {
                'Authorization': 'Bearer ' + accessToken,
                'cache-control': 'no-cache'
            },
            data: courseInfo,
            method: 'get',
            success: function (data) {
                callback(data);
            },
            error: function (data) {
                console.log("error: " + JSON.stringify(data));
                if (data.status === 401) {
                    enroll(uid, accessToken, callback);
                } else {
                    err(data);
                }
            },
            complete: function () {
                $('#spinner').hide();
            }
        });
    });
}

/**
 * @brief Build an HTML data containing stats data
 * @param courseData dictionary containing stats
 * @returns {*|jQuery|HTMLElement}
 */
function makeOverviewTable(classes) {

    var keys = [];
    for (var key in classes) {
        if (classes.hasOwnProperty(key)) keys.push(key);
    }

    var $table = $('<table/>');
    $table.append('<tr>' +
    '<th> Course </th>' +
    '<th> Today </th>' +
    '<th> This Week </th>' +
    '<th> All Time </th>' +
    '</tr>');
    $table.addClass('bordered');

    for(var i=0; i<keys.length; i++){

        var key = keys[i];
        var data = classes[key];

        if(data.archived) {
            key = key +  '<span class="badge new" data-badge-caption="Archived"></span>'
        }

        $table.append( '<tr>' +
            '<td>' + key + '</td>' +
            '<td>' + data.day + '</td>' +
            '<td>' + data.week + '</td>' +
            '<td>' + data.total + '</td>' +
            '</tr>');
    }
    return $table;
}

/**
 * @brief Build an HTML data containing tone data
 * @param courseData dictionary containing stats
 * @returns {*|jQuery|HTMLElement}
 */
function makeGenericTable(classes) {

    var keys = [];
    for (var key in classes) {
        if (classes.hasOwnProperty(key)) keys.push(key);
    }

    var $table = $('<table/>');
    $table.append('<tr>' +
    '<th> Attribute </th>' +
    '<th> Score </th>' +
    '</tr>');
    $table.addClass('bordered');

    for(var i=0; i<keys.length; i++){

        var key = keys[i];
        var data = classes[key];

        $table.append( '<tr>' +
            '<td>' + key + '</td>' +
            '<td>' + data + '</td>' +
            '</tr>');
    }
    return $table;
}

/**
 * @brief Create a greating based on current time
 * @returns {{phrase: string, title: string}}
 */
function makeGreeting() {
    var now = new Date();
    var tod = "";

    // After 3am and before noon is morning
    if(now.getHours() > 3 && now.getHours() < 12) {
        tod = "morning";
    } else if(now.getHours() < 17) {
        // before 5pm is afternoon
        tod = "afternoon";
    } else {
        tod = "evening";
    }

    return {
        phrase: "Good " + tod,
        title: document.title
    };
}

/**
 * @brief Handles fetching remote data and building out UI
 * @param packed course and user parameters
 * @param err callback function receives raw AJAX error
 */
function setGreeting(packed, retry, err) {

    fetchStats(packed['edu_id'], packed['auth_id'], function (courseData) {

        var username = (typeof courseData.nickname === 'undefined') ? '' : ', ' + courseData.nickname;
        var info = makeGreeting();

        $(".greeting").text(info.phrase + username);

        $('#main-content').show();
        $('#main-content').empty().append('<span class="gray-text text-darken-2">Your Piazza</span>');

        if(Object.keys(courseData).length > 0) {
            $('#engagement').append(makeOverviewTable(courseData['stats']));
            $('#quality').append(makeGenericTable(courseData['quality']));
            $('#tone').append(makeGenericTable(courseData['tone']));
        } else if (retry > 0) {
            console.error("Class data is not yet ready");

            setTimeout(setGreeting, 500, packed, retry-1, err);
        }
    }, err);
}

function scrapeCoursePageInfo(callback) {
     chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
         var activeTab = tabs[0];
         if (activeTab) {
             var title = activeTab.title;
             var url = activeTab.url;

             var courseName = title.split('(')[0];
             var courseId = url.split('/')[4];
             if(courseId.indexOf('?') >= 0) {
                 courseId = courseId.split('?')[0];
             }

             console.debug("Course Info: " + courseName, courseId);

             callback({'coursename' : courseName, 'courseid' : courseId });

         } else {
             console.error("Failed to get course data from current tab, using mock data");
             callback({'coursename' : 'OMS CS6460', 'courseid' : 'j6azklk4gaf4v9' });
         }
     });
}

/**
 * Holy cow, we have a verified user and a site cookie! Load up the details
 * @param cookie LTS cookie
 * @param idToken User token for backend auth
 */
function loadUserDetails(cookie, idToken, err) {

    // Make sure the login div is hidden
    $('#user-details-container').hide();

    // TODO refactror in object
    var packed = {
        'edu_id' : cookie.value,
        'auth_id' : idToken
    };

    console.debug("Req: " + packed);
    setGreeting(packed, 1, err);
}

/**
 * Start the auth flow and authorizes to Firebase.
 * @param{boolean} interactive True if the OAuth flow should request with an interactive mode.
 */
function startAuth(interactive) {

    console.debug("Starting auth mode: " + interactive);

    // Request an OAuth token from the Chrome Identity API.
    chrome.identity.getAuthToken({ interactive: !!interactive }, function(token) {
        if (chrome.runtime.lastError && !interactive) {

            console.debug('It was not possible to get a token programmatically.');
            $('#login-button').removeAttr("disabled");

        } else if (chrome.runtime.lastError) {

            console.error(chrome.runtime.lastError);
            $('#login-button').removeAttr("disabled");

        } else if (token) {

            // Authrorize Firebase with the OAuth Access Token.
            var credential = firebase.auth.GoogleAuthProvider.credential(null, token);
            firebase.auth().signInWithCredential(credential).catch(function(error) {

                // The OAuth token might have been invalidated. Lets' remove it from cache.
                if (error.code === 'auth/invalid-credential') {
                    chrome.identity.removeCachedAuthToken({ token: token }, function() {
                        startAuth(interactive);
                    });
                }
            });

            $('#login-button').removeAttr("disabled");

        } else {

            console.error('The OAuth Token was null');
            $('#login-button').removeAttr("disabled");

        }
    });
}

/**
 * Because every god damn JS API is async now
 * @param idToken token from the logged in user
 */
function excessiveCallbacks(idToken) {
    chrome.cookies.get({"url": "https://piazza.com", "name": "last_piaz_user"}, function (cookie) {
        loadUserDetails(cookie, idToken, function(error) {
            console.error(error);
        });
    });
}

/**
 * Called when auth state change is triggerd
 * @param user Logged in user or logged out user (if user null)
 */
function handleAuthChange(user) {

    console.debug("Auth change: " + JSON.stringify(user));

    if(!user)
    {
        // Clicking the login button(s) will initiate the enroll flow and then the
        // get stats flow
        $("#greeting").text("Welcome! Sign-in to begin!");
        $('#login-button').show();
        $('#login-button').removeAttr("disabled");

        return;
    }

    $('#spinner').show();
    user.getIdToken().then(excessiveCallbacks);
}

/**
 * Starts the sign-in process.
 */
function startSignIn() {

  $('#login-button').attr("disabled", "disabled");

  // Enable interactive mode if we have no authorization token on user
  startAuth(!firebase.auth().currentUser);

}

/**
 * On DOM load, begin the authorization check
 */
function initApp() {

    // Callback for when user logs in/out
    firebase.auth().onAuthStateChanged(handleAuthChange);

    // If we have a valid current user, start the auth process
    // in non-interactive mode to trigger data load
    if (firebase.auth().currentUser) {

        console.debug("Current user is valid");
        startAuth(false);

    } else {

        console.debug("No current user");
    }
};

window.onload = function() {

    $('#login-button').hide();

    excessiveCallbacks('mock');

    //$('#login-button').click('click', startSignIn);

    initApp();
};