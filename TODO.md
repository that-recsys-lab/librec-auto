### librec-auto TODO

- Upgrade to LibRec 3.0 (harder than we thought)
- clean up / document
- platform-sensitive install (paths for Java, Python)
- Separate LibRec install (or detect)
- sanity check on eval-only: has the config changed too much?
- detect: item-based similarity vs user-based, detect ranking vs prediction metrics
x P-Fairness metrics (LibRec)
x C-Fairness metrics (LibRec)
x Configuration includes
- Interface to other systems: PSL, LibFM
- Sub-group metrics (long-tail, protected group, etc.)
- Fix status mechanism to stay up-to-date with different manipulations
- Prompt in purge command should be specific about what will be removed.
- Imlement RelaxNG schemas and validation

### librec-auto BUGS
- check command does not catch missing data file or missing metric class

### librec-auto UNTESTED
- library functionality is only minimally tested

### librec-auto LIMITATIONS
- studies can't range over values in no-parse elements (rerankers)
- studies can't compare different algorithms
- libraries don't have true inheritance


