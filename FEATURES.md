# NativeScript Tooling Tests

## Framework Features

### Core
- [x] No dependencies on internal network shares
- [x] Execute command to return not only output, but also exit code, pid and others.
- [x] Multiple simultaneous emulators and simulators 
- [x] Improve Test Settings
   - [x] Split on multiple sub-classes
   - [ ] Comply on 100% with ns-ci-build-tool variables
- [x] Logger and Reporting
   - [x] No more print statements
   - [ ] More clear logs
   - [ ] Respect logging levels (be able to configure logger verbosity)
   - [ ] Generate HTML report with screenshots and links to artifacts on test fail (may be Allure)
- [ ] Run tests via nose command
- [x] Base TnsTest
- [x] Utils wrapping tools we need
   - [X] Xcode
   - [X] Gradle
   - [X] Java
   - [X] Git
   - [X] Npm
   - [ ] Chrome browser
- [x] Image utils
   - [X] Get pixels by color
   - [X] Get main color
   - [ ] Picture comparison
   - [ ] Picture matching by template matching
- [x] Wait helper
   - [X] Wait until function returns true or timeout reached
- [x] TestContext to hold
   - [ ] Started pids
   - [ ] App under test (to be able to backup it on test fail)
   - [ ] Started emulators, simulators or device ids (to be able to take picture on fail)
- [x] Tests for core itself
- [ ] Docs
    - [ ] Docstring everywhere
    - [ ] Accurate readme and other mds.
    
### Data
- [ ] Data for apps and templates (including change sets)

### Products
- [ ] Wrapper around `tns` commands
- [ ] TnsAsserts util to verify `tns` command do what is supposed to do.

## Tests

### {N} CLI Functional Tests
- [ ] Write all the tests

### {N} CLI Performance Tests

Acceptance Criteria:
- Measure following things on HelloWorldJS, HelloWorldNG and MasterDetailsNG templates:
- [X] Project create
- [X] Platform add (both platforms)
- [X] Initial and incremental prepare (both platforms)
- [X] Initial and incremental build (both platforms)
- [X] Initial and incremental build (both platforms)
- [ ] Time to apply JS/TS/CSS/XML/HTML (both platforms)

Notes:
Build, prepare and sync tests should be done with and without bundle for (at lest) following templates:
- [X] HelloWorldJS
- [X] HelloWorldNG
- [ ] HelloWorldVue
- [X] MasterDetailsNG

### Code Sharing Story Tests
- [ ] Write all the tests

### Monitor Live Apps & Templates

We need to make sure we always work out of the box for end users.

Acceptance Criteria:
- User should be able to git clone and run all popular app.
- User should be able to create app from any template and run it without any modifications.
- Run should also pass with bundle if webpack is available in the app/template.

- [ ] JS SDK Samples
- [ ] NG SDK Samples
- [ ] Groceries
- [ ] QSF

- [ ] Hello Wolrd Templates
- [ ] SideKick Templates (including blank and health)
- [ ] Vue Templates