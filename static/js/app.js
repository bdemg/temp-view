$(document).foundation()

var app = angular.module('TempView', ['angular.filter', 'ngMaterial']);
app.config(function($interpolateProvider){
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
}).run();
