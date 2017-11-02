"use strict";
exports.__esModule = true;
var fs_1 = require("fs");
var yargs_1 = require("yargs");
// This is good for local dev environments, when it's better to
// store a projects environment variables in a .gitignore'd file
require('dotenv').config();
// Would be passed to script like this:
// `ts-node set-env.ts --environment=dev`
// we get it from yargs's argv object
var environment = yargs_1.argv.environment;
var isProd = environment === 'prod';
var targetPath = "./src/environments/environment." + environment + ".ts";
var envConfigFile = "\nexport const environment = {\n  production: " + isProd + ",\n  auth0clientID: '" + process.env.AUTH0_CLIENT_ID + "',\n  auth0domain: '" + process.env.AUTH0_DOMAIN + "',\n  auth0audience: '" + process.env.AUTH0_AUDIENCE + "'\n};\n";
fs_1.writeFile(targetPath, envConfigFile, function (err) {
    if (err) {
        console.log(err);
    }
    console.log("Output generated at " + targetPath);
});
