concat = ->
  tmp = []
  for array in arguments
    tmp = tmp.concat(array)
  tmp

bannerBundle = '''
/*! Snorky JS connector (bundle) | http://snorkyproject.org/ | MPL License
 *  Includes other software:
 *   - my.class.js | https://github.com/jiem/my-class | MIT License
 *   - js-signals | http://millermedeiros.github.io/js-signals/ | MIT License */
'''
bannerStandalone = '''
/*! Snorky JS connector | http://snorkyproject.org/ | MPL License */
'''

module.exports = (grunt) ->
  grunt.loadNpmTasks "grunt-contrib-concat"
  grunt.loadNpmTasks "grunt-contrib-jasmine"
  grunt.loadNpmTasks "grunt-karma"
  grunt.loadNpmTasks "grunt-contrib-jshint"
  grunt.loadNpmTasks "grunt-contrib-watch"
  grunt.loadNpmTasks "grunt-contrib-uglify"

  libFiles = [
    "lib/*.js"
  ]

  modernLibFiles = [
    "lib/my.class.js"
    "lib/promise.js"
    "lib/signals.js"
  ]

  srcFiles = [
    "src/stable-stringify.js"
    "src/snorky.js"
    "src/services/base.js"
    "src/services/messaging.js"
    "src/services/pubsub.js"
    "src/services/datasync.js"
    "src/services/chat.js"
    "src/services/cursors.js"
  ]

  specUtils = [
    "src/spec/utils/it-promise.js"
    "src/spec/utils/spy-signal.js"
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
      standalone:
        src: srcFiles
        dest: "build/snorky.js"
        options:
          stripBanners:
            line: yes
          banner: bannerStandalone
      bundle:
        src: concat(modernLibFiles, srcFiles)
        dest: "build/snorky.bundle.js"
        options:
          stripBanners:
            line: yes
          banner: bannerBundle
    uglify:
      standalone:
        files:
          "build/snorky.min.js": srcFiles
        options:
          sourceMap: yes
          banner: bannerStandalone
      bundle:
        files:
          "build/snorky.bundle.min.js": concat(modernLibFiles, srcFiles)
        options:
          sourceMap: yes
          banner: bannerBundle
    watch:
      test:
        files: ["src/**/*.js", "gruntfile.coffee"]
        tasks: ["jasmine"]
        options:
          atBegin: true

  grunt.registerTask "test", ["jshint", "jasmine"]
  grunt.registerTask "default", ["test"]
  grunt.registerTask "build", [
    "concat:standalone"
    "concat:bundle"
    "uglify:standalone"
    "uglify:bundle"
  ]
  return
