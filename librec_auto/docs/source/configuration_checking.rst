============
Configuration file checking
============

Ensuring you're all set with Check
--------------------

Once you've setup your study's directory, you can ensure that your study is ready to compile by running the ``Check`` command.
The check command will read over your configuration file, a log file that's created by ``LibRec``, and a log file that's created by ``libRec-auto`` and append the found errors and messages
to your ``output.xml`` file.

These checks are performed in the course of running a study regardless, but you have the ability to check your setup and debug it in advance.

There are various things the ``"check"`` command will check:

**Environment:**

* Java version: Checks that you have Java version at least 1.8. (Note that it is difficult to do this in a general way and some JDKs are not recognized. You can skip this check with the ``-nj`` flag and the system will not complain about JDK compatibility.)

**Configuration file checks:**

* Access: ensure all directories that ``LibRec`` or ``LibRec-Auto`` could write to have write access.
* Elements: ensure all necessary elements for ``LibRec`` are found in the configuration file.
* Library: ensure supplied library can be found and loaded.
* Data: ensure supplied data directory can be found and loaded.
* Scripts: ensure all paths to scripts are valid.
* Optimization: ensure configuration file is setup to run optimization experiments. 

**LibRec checks (from Java):**

* On the Java side, the class names of algorithms and metrics are checked.
* If an error is thrown during the execution of LibRec, the exception will be caught and added to output.xml
 
**LibRec-Auto Log check (from Python):**

Using the ``"-dev"`` argument in the command line will change the level of debugging messages you see in  output.xml. Use the argument to set the logging level to ``DEBUG``, which will catch all ``INFO`` logging messages. 
Without the ``"-dev"`` argument, the output xml file will only show ``WARNING`` messages and above. 

* ``"LibRec-Auto_Log"``: LibRec-Auto_Log will include all messages from ``logging`` messages. These messages will follow this general pattern: ``{log-level}:root:{message}``. The levels can be broken down as such:
    * ``ERROR``: Error level messages appear when there is a problem that will not allow LibRec-Auto to compile correctly. 
    * ``WARNING``: Warning level messages appear when there is a problem, but the problem will not interfere with LibRec-Auto's compilation.
    * ``INFO``: Info level messages appear when LibRec-Auto creates or writes to directories and files on the user's computer.