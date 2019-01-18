# NativeScript CLI Tests Folder Structure

### Smoke tests

`smoke` folder contains set smoke tests that are executed on PRs.

On commit in master we run:
```bash
python run_ns.py tests\cli --exclude="^test_[2-9]"
```

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