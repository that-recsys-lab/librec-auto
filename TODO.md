* librec-auto TODO

- Update to Python 3
- Upgrade to LibRec 3.0
- clean up / document
- multiple post scripts
- platform-sensitive install (paths for Java, Python)
- script runs in any directory
- Separate LibRec install (or detect)
- sanity check on eval-only: has the config changed too much?
- detect: item-based similarity vs user-based, detect ranking vs prediction metrics
- AutoPath object to avoid path issues in future
- Support for re-ranking algorithms (base recommender plus re-ranker)
- P-Fairness metrics (LibRec?)
- C-Fairness metrics (LibRec?)
- Configuration includes
- Interface to other systems: PSL
- Sub-group metrics (long-tail, protected group, etc.)

* librec-auto BUGS
- configuration is read from main directory conf/config.xml even when different -c path is specified.
- JAR file not found when working directory other than librec_auto main.
