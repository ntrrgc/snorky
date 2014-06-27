concat = ->
  tmp = []
  for array in arguments
    tmp = tmp.concat(array)
  tmp

module.exports = (grunt) ->
  grunt.loadNpmTasks "grunt-contrib-concat"
  grunt.loadNpmTasks "grunt-contrib-jasmine"
  grunt.loadNpmTasks "grunt-karma"

  libFiles = [
    "lib/*.js"
  ]

  srcFiles = [
    "src/snorky.js"
    "src/services/base.js"
    "src/services/messaging.js"
  ]

  specFiles = [
    "src/spec/**.spec.js"
  ]

  grunt.initConfig
    jasmine:
      src: concat(libFiles, srcFiles)
      options:
        specs: specFiles
    karma:
      unit:
        options:
          files: concat(libFiles, srcFiles, specFiles)
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
    concat:
      src:
        src: srcFiles
        dest: "build/snorky.js"

  grunt.registerTask "test", ["jasmine"]
  grunt.registerTask "default", ["test"]
  grunt.registerTask "build", ["concat:src"]
  return
