module.exports = (grunt) ->
  grunt.loadNpmTasks "grunt-contrib-jasmine"
  grunt.loadNpmTasks "grunt-karma"

  grunt.initConfig
    jasmine:
      src: [
        "lib/lodash.compat.js"
        "lib/json3.lib.js"
        "lib/my.class.js"
        "lib/promise.js"
        "src/snorky.js"
        "src/services.js"
      ]
      options:
        specs: "src/spec/**.spec.js"
    karma:
      unit:
        options:
          files: [
            "lib/*.js"
            "src/snorky.js"
            "src/services.js"
            "src/spec/**.spec.js"
          ]
          browsers: [
            "IE6 - WinXP"
            "IE8 - WinXP"
            "Chrome"
            "Firefox"
          ]
          frameworks: ["jasmine"]
          reporters: ["progress", "growl"]
          singleRun: false
          autoWatch: true

  grunt.registerTask "test", ["jasmine"]
  grunt.registerTask "default", ["test"]
  return
