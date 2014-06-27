module.exports = (grunt) ->
  grunt.loadNpmTasks "grunt-contrib-jasmine"
  grunt.loadNpmTasks "grunt-karma"

  srcFiles = [
    "lib/*.js"
    "src/snorky.js"
    "src/services/base.js"
    "src/services/messaging.js"
  ]

  grunt.initConfig
    jasmine:
      src: srcFiles
      options:
        specs: "src/spec/**.spec.js"
    karma:
      unit:
        options:
          files: srcFiles.concat(["src/spec/**.spec.js"])
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
