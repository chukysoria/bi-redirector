// public/app.js

$(document).ready(function() {
  var auth = new auth0.WebAuth({
    domain: 'biredirect.eu.auth0.com',
    clientID: 'CPzBGfaoA9XYJTOAqHVktZXySW8iVu49'
   });


    $('.btn-login').click(function(e) {
      e.preventDefault();
      auth.authorize({
        audience: 'https://' + 'biredirect.eu.auth0.com' + '/userinfo',
        scope: 'openid profile',
        responseType: 'code',
        redirectUri: 'http://localhost:5000/api/authcallback'
      });
    });
});  