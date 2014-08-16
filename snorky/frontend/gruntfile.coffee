concat = ->
  tmp = []
  for array in arguments
    tmp = tmp.concat(array)
  tmp

module.exports = (grunt) ->
  grunt.loadNpmTasks "grunt-contrib-concat"
  grunt.loadNpmTasks "grunt-contrib-jasmine"
  grunt.loadNpmTasks "grunt-karma"
  grunt.loadNpmTasks "grunt-contrib-jshint"

  libFiles = [
    "lib/*.js"
  ]

  srcFiles = [
    "src/stable-stringify.js"
    "src/snorky.js"
    "src/services/base.js"
    "src/services/messaging.js"
    "src/services/pubsub.js"
    "src/services/datasync.js"
    "src/services/chat.js"
  ]

  specUtils = [
    "src/spec/utils/**.js"
  ]

  specFiles = [
    "src/spec/**.spec.js"
  ]

  grunt.initConfig
    jasmine:
      src: concat(libFiles, srcFiles, specUtils)
      options:
        specs: specFiles
    karma:
      server:
        options:
          files: concat(libFiles, srcFiles, specUtils, specFiles)
          frameworks: ["jasmine"]
          reporters: ["progress"]
          singleRun: false
          autoWatch: true
      auto:
        options:
          files: concat(libFiles, srcFiles, specFiles)
          browsers: [
            "IE6 - WinXP"
            "IE8 - WinXP"
            "Chrome"
            "Firefox"
          ]
          frameworks: ["jasmine"]
          reporters: ["progress"]
          singleRun: false
          autoWatch: true
    jshint:
      src: srcFiles
      options:
        force: true
    concat:
      src:
        src: srcFiles
        dest: "build/snorky.js"

  grunt.registerTask "test", ["jshint", "jasmine"]
  grunt.registerTask "default", ["test"]
  grunt.registerTask "build", ["concat:src"]
  return
