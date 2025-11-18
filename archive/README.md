# Archive Directory

This directory contains old development, debug, and verification files that were used during the creation of Toshokan-Codo but are no longer needed for normal operation.

## Contents

### Debug Test Files
- `test_debug_validator.py` - Debug test for visual validator
- `test_fixer_quick.py` - Quick fixer test
- `test_manual_validator.py` - Manual validator test
- `test_overflow_debug.py` - Overflow detection debug test
- `test_quick_validator.py` - Quick validator test

**Note:** All proper tests are in the `tests/` directory. These were ad-hoc debug scripts.

### Verification Scripts
- `verify_complete_system.py` - System-wide integration verification
- `verify_fixer.py` - Fixer module verification
- `verify_output_manager.py` - Output manager verification
- `verify_validator.py` - Validator verification

**Note:** End-to-end tests are in `tests/test_end_to_end.py`. These were development verification scripts.

### Output Files
- `test_output.txt` - Old test output logs

### Documentation
- `INTENT_PARSER_EXAMPLES.md` - Intent parser usage examples (info now in main README)

## Why Archived?

These files were created during development checkpoints for debugging and manual verification. Now that the project has:
- 99 automated tests in `tests/`
- Complete documentation in README.md
- Proper test coverage for all modules

...these ad-hoc scripts are no longer necessary for normal development or usage.

## Can I Delete This Directory?

Yes. If the main test suite (`tests/`) passes and you don't need historical development artifacts, this entire directory can be safely deleted.

To run the proper tests:
```bash
python -m pytest tests/
```

Or run individual test files:
```bash
python tests/test_intent_parser.py
python tests/test_component_mapper.py
# etc.
```
