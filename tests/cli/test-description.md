# NativeScript CLI Tests Folder Structure

### Smoke tests

`smoke` folder contains set smoke tests (to be executed on variety of node and java versions) plus set of tests for pr.

**pr_tests.py**
- Tests executed on PRs in {N} CLI repo.

**smoke_tests.py**
- Tests executed on commit in master branch.
- Note that those tests are also executed nightly on variety of node and java versions.


### Tests for CLI Commands

### build

Tests for `tns platform add/list/remove/update` commands.

Tests for `tns prepare` and `tns build` commands.

Tests for `tns install` command.

### create

Tests for `tns create` and `tns init` commands.

### debug

Tests for `tns debug` command.

### misc

Tests for `tns appstore` command.

Tests fot `tns autocomplete`.

Tests for `tns doctor`.

Tests for `tns help <command>`.

Tests for `tns proxy`.

Tests for `tns setup`.

Tests for `usage-reporting` and `error-reporting` commands

### plugin
Tests for `tns plugin` command.

### preview
Tests for `tns preview` command.

### resources
Tests for `resources update` command.

### run
Tests for `tns run`, `tns deploy` and `tns device` commands.

### test
Tests for `tns Tests init` and `tns test` commands.
   
### update
Tests for `update` command.